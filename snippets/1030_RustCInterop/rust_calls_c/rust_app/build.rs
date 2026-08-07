// Compiles ../c_lib/mathlib.c with the `cc` crate and statically links it
// into this binary. `cc` picks a cross-compiler automatically based on the
// Cargo target triple (e.g. arm-none-eabi-gcc for thumbv7em-none-eabihf),
// as long as that compiler is on PATH.
fn main() {
    cc::Build::new()
        .file("../c_lib/mathlib.c")
        .include("../c_lib")
        .flag_if_supported("-ffreestanding") // no hosted libc assumed
        .flag_if_supported("-fno-builtin")
        .compile("mathlib");

    println!("cargo:rerun-if-changed=../c_lib/mathlib.c");
    println!("cargo:rerun-if-changed=../c_lib/mathlib.h");
}
