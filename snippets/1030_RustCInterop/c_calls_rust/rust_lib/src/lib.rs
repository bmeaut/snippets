//! no_std Rust static library, called from a hosted C program.
//!
//! `no_std` removes the Rust standard library (allocator, threads, OS I/O,
//! panic unwinding machinery, etc.) and leaves only `core`, which assumes
//! nothing about the host - the same posture an embedded target needs.
//! Because there's no `std`, two things a hosted program gets for free
//! must be supplied by hand: a panic handler, and (if the profile isn't
//! `panic = "abort"`) an unwinding personality function.
#![no_std]

use core::panic::PanicInfo;

// With no_std there is no default panic handler. This one must exist
// exactly once in the final link. It can never return (`-> !`), matching
// the fact that Rust has no way to recover from a panic without std.
#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    loop {}
}

// `#[repr(C)]` pins the field layout to the C ABI: fields stay in
// declaration order with C's alignment/padding rules. Plain Rust structs
// have NO such guarantee - the compiler is free to reorder fields or
// change layout between compiler versions to reduce padding. Any type
// crossing the FFI boundary by value or by pointer must be `repr(C)`
// (or a `#[repr(transparent)]`/primitive type that maps 1:1 to a C type).
#[repr(C)]
pub struct Point {
    pub x: i32,
    pub y: i32,
}

// `extern "C"` fixes the calling convention (argument registers/stack,
// return-value location) to match what a C compiler emits/expects.
// `#[no_mangle]` turns off Rust's name mangling so the C linker can find
// the symbol by its literal name (otherwise it would be mangled into
// something like `_ZN8rust_lib8rust_add17h...E`).
#[no_mangle]
pub extern "C" fn rust_add(a: i32, b: i32) -> i32 {
    a.wrapping_add(b)
}

#[no_mangle]
pub extern "C" fn rust_point_distance_sq(p: Point) -> i64 {
    let dx = i64::from(p.x);
    let dy = i64::from(p.y);
    dx * dx + dy * dy
}

// Pointer + length instead of a Rust slice/&str: C has no concept of a
// fat pointer, so a `&[u8]` (ptr+len bundled together) cannot cross the
// FFI boundary as-is. It must be decomposed into a raw pointer and a
// length that C already understands.
//
// # Safety
// `data` must be non-null and point to at least `len` valid, readable
// bytes for the duration of the call - the same contract a C function
// taking `(const uint8_t *data, size_t len)` would document.
#[no_mangle]
pub unsafe extern "C" fn rust_sum_bytes(data: *const u8, len: usize) -> u32 {
    if data.is_null() {
        return 0;
    }
    let slice = core::slice::from_raw_parts(data, len);
    slice.iter().fold(0u32, |acc, &b| acc + u32::from(b))
}
