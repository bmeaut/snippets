//! Bare-metal `no_std` Rust "firmware" for a Cortex-M target, calling into
//! a small C library (../c_lib/mathlib.c) via FFI.
//!
//! Unlike c_calls_rust (a no_std *library* dropped into a hosted C
//! program), this crate IS the whole program: there is no libc, no OS,
//! no crt0. Rust normally gets a `_start`/`main` entry point and a
//! runtime from `std`; `#![no_main]` says "don't generate any of that,
//! I'm providing my own", so this file supplies the reset handler and
//! vector table by hand instead of depending on the `cortex-m-rt` crate
//! (which normally does this for you) - the point is to show what that
//! crate is actually doing under the hood.
#![no_std]
#![no_main]

use core::panic::PanicInfo;

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    loop {}
}

// Declared in ../c_lib/mathlib.h, compiled and linked in by build.rs.
extern "C" {
    fn c_add(a: i32, b: i32) -> i32;
    fn c_toggle_bits(pattern: u32) -> u32;
}

// Symbols defined by memory.x, marking the .bss/.data regions that need
// zero-initializing / copying from flash before any Rust code that might
// touch a `static` can safely run.
extern "C" {
    static mut _sbss: u8;
    static mut _ebss: u8;
    static mut _sdata: u8;
    static mut _edata: u8;
    static _sidata: u8;
}

/// The reset handler: the very first code the CPU runs after power-on.
/// It must initialize RAM before calling into any Rust that might use a
/// `static`, because `.bss`/`.data` are not valid yet - this is normally
/// invisible because a hosted OS's crt0 does it before `main` ever runs.
///
/// # Safety
/// Must only ever be invoked once, by the CPU, as the reset vector - it
/// assumes RAM is uninitialized garbage and unconditionally overwrites
/// the `.bss`/`.data` regions described by `memory.x`.
#[no_mangle]
pub unsafe extern "C" fn Reset() -> ! {
    let bss_start = &raw mut _sbss;
    let bss_end = &raw mut _ebss;
    let bss_len = bss_end as usize - bss_start as usize;
    core::ptr::write_bytes(bss_start, 0, bss_len);

    let data_start = &raw mut _sdata;
    let data_end = &raw mut _edata;
    let data_len = data_end as usize - data_start as usize;
    let data_src = &raw const _sidata;
    core::ptr::copy_nonoverlapping(data_src, data_start, data_len);

    main()
}

// The Cortex-M vector table's second word (index 1) must hold the reset
// handler's address. `#[link_section]` places this exactly where
// memory.x's `.vector_table` section expects it; `KEEP` in the linker
// script stops the linker from discarding it as "unused" (nothing else
// in the program references it - the CPU reads it directly out of flash).
#[link_section = ".vector_table.reset_vector"]
#[no_mangle]
pub static RESET_VECTOR: unsafe extern "C" fn() -> ! = Reset;

fn main() -> ! {
    // SAFETY: c_add/c_toggle_bits are plain pure functions on plain
    // integers - no pointers, no shared state, so the FFI call has no
    // preconditions beyond "the C library was linked in", which build.rs
    // guarantees.
    let sum = unsafe { c_add(2, 3) };
    let toggled = unsafe { c_toggle_bits(0xF0F0_F0F0) };

    // No OS, no stdout: there's nowhere to "print" to. Stash results in
    // a static so they're observable in a debugger/memory dump, the same
    // way you'd stage a value for a peripheral register on real hardware.
    static mut RESULT: (i32, u32) = (0, 0);
    unsafe {
        RESULT = (sum, toggled);
        core::ptr::read_volatile(&raw const RESULT);
    }

    loop {
        cortex_m_wfi();
    }
}

/// Issues the Cortex-M `wfi` (wait-for-interrupt) instruction to idle the
/// CPU instead of spinning hot in the final `loop {}`.
#[inline(always)]
fn cortex_m_wfi() {
    unsafe {
        core::arch::asm!("wfi");
    }
}
