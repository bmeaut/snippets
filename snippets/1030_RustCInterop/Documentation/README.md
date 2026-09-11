# Rust ⇄ C interop in embedded systems

Two minimal, size-focused `no_std` examples, one per direction:

| Directory | Direction | What it shows |
|---|---|---|
| [`c_calls_rust/`](c_calls_rust) | C `main()` calls into a Rust `no_std` static library | Rust as a **library** dropped into an existing C-based firmware/build |
| [`rust_calls_c/`](rust_calls_c) | Rust `no_std`, `no_main` firmware calls into a C library | Rust as the **whole program**, with C as a leaf dependency |

Both were built with `cargo`/`rustc` 1.93.1 on this machine, and **both are
fully built, linked, and run-verified** — `c_calls_rust` as a native
Windows executable (verified stdout below), `rust_calls_c` as a real
Cortex-M4 ELF booted under QEMU (`qemu-system-arm -M lm3s6965evb`), verified
by halting at a breakpoint and reading the computed values straight out of
RAM (details in [§3](#3-rust_calls_c-bare-metal-no_std-rust-firmware-calling-a-c-library)).

---

## 1. Rust vs C memory layout

This is the part that actually matters for interop — get it wrong and you
get silent corruption, not a compile error.

### Struct/field layout

- **C**: fields are laid out in declaration order, padded per the platform's
  ABI (e.g. System V AMD64 or the ARM AAPCS) so each field sits at its
  natural alignment. This layout is part of the ABI contract — any compiler
  targeting that platform must agree on it.
- **Rust (default, `repr(Rust)`)**: the compiler is explicitly free to
  **reorder fields, add hidden padding, or change the layout entirely**
  between compiler versions to shrink the type or improve access patterns.
  There is no stability guarantee — two builds of the same crate with
  different rustc versions may lay a struct out differently.
- **Crossing the FFI boundary**: any Rust type shared with C — by value, by
  pointer, or embedded in another shared type — must be `#[repr(C)]` (see
  [`rust_lib/src/lib.rs`](c_calls_rust/rust_lib/src/lib.rs)'s `Point`),
  `#[repr(transparent)]` for a single-field wrapper, or a bare primitive
  that maps 1:1 onto a C type (`i32`↔`int32_t`, `usize`↔`size_t`, etc.).
  `repr(C)` reproduces C's field-order-preserving, natural-alignment layout
  exactly.

### Pointers and "fat" references

- **C** pointers are always a single machine word: address only. A
  C-style string or buffer needs a side channel for length (NUL
  termination, or an explicit `len` parameter).
- **Rust** references/pointers to dynamically-sized types (`&[T]`, `&str`,
  `&dyn Trait`) are **fat pointers** — two words: address + length (or
  address + vtable pointer for trait objects). A fat pointer has no C
  equivalent and cannot cross the FFI boundary as-is.
  [`rust_sum_bytes`](c_calls_rust/rust_lib/src/lib.rs) shows the fix: split
  a would-be `&[u8]` into a raw pointer (`*const u8`) plus an explicit
  `len: usize`, exactly like a C function's `(const uint8_t *, size_t)`
  signature.

### Enums, `Option`, and tagged unions

- **C** has no tagged union built in — you hand-roll a struct with a
  discriminant field plus a `union` and remember to check the tag yourself.
  Nothing stops you from reading the wrong union member.
- **Rust** enums are compiler-checked tagged unions, but their memory
  layout is *not* C-compatible by default (variant order/discriminant
  width can change). `#[repr(C)]` on an enum makes it lay out like a C
  tagged struct-union. Plain `#[repr(Rust)]` enums (including `Option<T>`)
  must never appear directly in an `extern "C"` signature.
- One Rust-specific optimization worth knowing: `Option<&T>` and
  `Option<Box<T>>` are **niche-optimized** to the same size as a bare
  pointer (`null` represents `None`) — genuinely convenient for FFI
  (`Option<extern "C" fn()>` is exactly one function-pointer word), but
  it's a Rust-layout detail, not something C's type system expresses.

### Stack, heap, and what "no_std" removes

- **C**: the stack is whatever the platform gives you; the heap is
  `malloc`/`free` via libc, backed by the OS. Both are simply *there* —
  freestanding C (no libc) is possible but nonstandard.
- **Rust with `std`**: stack works the same way; heap allocation
  (`Box`, `Vec`, `String`) goes through a global allocator that ultimately
  calls into the OS.
- **Rust with `#![no_std]`** (used in both examples here): the `alloc`
  crate, threads, files, `std::sync` primitives, and the default panic
  handler are all gone — only `core` remains, which assumes nothing about
  the host. This is precisely the embedded posture: no OS to lean on.
  Two consequences show up directly in the code:
  - A `#[panic_handler]` must be supplied by hand
    ([`rust_lib/src/lib.rs`](c_calls_rust/rust_lib/src/lib.rs),
    [`rust_app/src/main.rs`](rust_calls_c/rust_app/src/main.rs)) — `core`
    defines *that a panic handler must exist* but not what it does.
  - No heap exists unless you add a global allocator explicitly (not done
    here) — both examples only use the stack and `static`s.

### Program startup ("who initializes RAM before `main`?")

This is the sharpest difference between the two example directions, and
it's *not* really a Rust-vs-C difference — it's a **hosted-vs-bare-metal**
one:

- In `c_calls_rust`, the C program is hosted: its libc's `crt0` zeroes
  `.bss`, copies `.data` from the image into RAM, sets up the stack, and
  only then calls `main`. The Rust static library plugs into an
  environment that's already fully initialized — it never needs to think
  about this.
- In `rust_calls_c`, the Rust binary *is* the whole program running on
  bare metal — there is no crt0, no OS, nothing before it. So
  [`rust_app/src/main.rs`](rust_calls_c/rust_app/src/main.rs)'s `Reset`
  handler does that RAM setup by hand: zero `.bss`, copy `.data` in from
  flash (positions defined in
  [`memory.x`](rust_calls_c/rust_app/memory.x)), *then* call `main()`.
  Until that runs, every Rust `static` is reading uninitialized flash-image
  garbage — which is why `Reset` must be the very first thing the CPU
  executes (wired in via the vector table, see the file for details).
  In a production project this is normally handled by the `cortex-m-rt`
  crate; it's done by hand here so the mechanism is visible.

### Calling convention & name mangling

- **C** functions are called using the platform's C ABI (e.g. AAPCS on
  ARM), and their symbol names in the object file are the function names
  as written (give or take a leading underscore, platform-dependent).
- **Rust** functions use an unstable, unspecified Rust calling convention
  by default, and their symbol names are *mangled* (encode the crate,
  module path, and a hash — e.g. `_ZN8rust_lib8rust_add17h...E`) so that
  generics and modules with the same short name don't collide.
- Every function crossing the boundary in both examples is marked
  `extern "C"` (forces the C calling convention) and `#[no_mangle]`
  (emits the literal name so the C/linker side can find it) — see any
  `#[no_mangle] pub extern "C" fn ...` in
  [`rust_lib/src/lib.rs`](c_calls_rust/rust_lib/src/lib.rs) or the
  `extern "C" { fn c_add(...); }` block in
  [`rust_app/src/main.rs`](rust_calls_c/rust_app/src/main.rs) (C needs no
  such annotation — it's already the ABI baseline both sides agree on).

---

## 2. `c_calls_rust`: C `main()` calling a `no_std` Rust static library

```
c_calls_rust/
├── rust_lib/            # no_std Rust crate, crate-type = staticlib
│   ├── Cargo.toml
│   └── src/lib.rs
└── c_app/
    ├── main.c
    └── rust_lib.h        # hand-written; generate with cbindgen in a real project
```

### Steps

1. **Build the Rust side as a static library**, for a target that matches
   your C compiler's architecture/ABI. On this machine `gcc` is 32-bit
   MinGW (`i686`), so:

   ```bash
   cd c_calls_rust/rust_lib
   rustup target add i686-pc-windows-gnu   # once
   cargo build --release --target i686-pc-windows-gnu
   ```

   This produces `target/i686-pc-windows-gnu/release/librust_lib.a`.
   (On Linux/macOS or with a 64-bit MinGW/MSVC toolchain, use
   `x86_64-unknown-linux-gnu`, `x86_64-pc-windows-gnu`, or
   `x86_64-pc-windows-msvc` instead — just make sure the Rust target and
   the C compiler agree on architecture and ABI, or the linker will fail
   to resolve symbols, exactly as it did here on the first attempt.)

2. **Compile and link the C program against it:**

   ```bash
   cd ../c_app
   gcc main.c -I. -L../rust_lib/target/i686-pc-windows-gnu/release \
       -lrust_lib -o app.exe -lws2_32 -luserenv
   ```

   (`-lws2_32 -luserenv` are Windows-only — MinGW's Rust target pulls in a
   couple of system libs for low-level runtime support even in a `no_std`
   crate; omit them on Linux/macOS.)

3. **Run it** — verified output on this machine:

   ```
   $ ./app.exe
   rust_add(2, 3)            = 5
   rust_point_distance_sq(p) = 25
   rust_sum_bytes(bytes)     = 15
   ```

   `app.exe` is 46 KB — the multi-megabyte `librust_lib.a` is an
   *archive* of object files; the linker only pulls in the handful of
   symbols `main.c` actually references, plus `panic_handler`.

### Real-embedded variant

For an actual microcontroller target instead of this desktop demo, the
only thing that changes is step 1's `--target` (e.g.
`thumbv7em-none-eabihf`) and step 2's compiler (`arm-none-eabi-gcc`
instead of desktop `gcc`) — the Rust source, the `#[repr(C)]`/`extern "C"`
boundary, and the `Cargo.toml` profile are unchanged. This pattern —
a `no_std` Rust static library linked into an existing C-based firmware
build — is the common way Rust gets introduced into an existing embedded
C codebase incrementally.

---

## 3. `rust_calls_c`: bare-metal `no_std` Rust firmware calling a C library

```
rust_calls_c/
├── c_lib/
│   ├── mathlib.h
│   └── mathlib.c
└── rust_app/
    ├── Cargo.toml
    ├── build.rs          # compiles c_lib/mathlib.c via the `cc` crate
    ├── memory.x           # linker script: flash/RAM layout, vector table
    ├── .cargo/config.toml # target + linker flags
    └── src/main.rs        # #![no_std] #![no_main]: hand-rolled reset handler
```

This one targets `thumbv7em-none-eabihf` (Cortex-M4) and QEMU's
`lm3s6965evb` machine rather than the desktop — a `no_std`, `no_main`
Rust binary has no OS under it, so unlike part 1 it needs its own vector
table and startup code (see the "Program startup" section above and the
comments in `main.rs`/`memory.x`), which only makes sense in a bare-metal
context.

### Prerequisites

Installed on this machine via:

```bash
rustup target add thumbv7em-none-eabihf
winget install --id Arm.GnuArmEmbeddedToolchain -e --source winget   # arm-none-eabi-gcc
winget install --id SoftwareFreedomConservancy.QEMU -e --source winget # qemu-system-arm
```

Both installers put their `bin/` directories somewhere `winget` chooses,
not automatically on `PATH` for an already-open shell. On this machine
that was:

```bash
export PATH="/c/Program Files (x86)/Arm GNU Toolchain arm-none-eabi/14.2 rel1/bin:/c/Program Files/qemu:$PATH"
```

(open a new terminal, or re-run that `export`, before the commands below —
adjust the toolchain version folder name if `winget` installs a newer one)

### Steps

1. **Compile the C library + Rust firmware together and link:**

   ```bash
   cd rust_calls_c/rust_app
   cargo build --release
   ```

   `build.rs` invokes `arm-none-eabi-gcc` to compile `../c_lib/mathlib.c`
   into a static lib and links it in automatically; `.cargo/config.toml`
   passes `-Tmemory.x` so the linker places `.vector_table`/`.text`/etc.
   where the MCU expects them. Output:
   `target/thumbv7em-none-eabihf/release/rust_app`, a **2 KB ELF image**
   (1070 bytes of `.text`, 8 bytes of `.bss`, 0 bytes of `.data` —
   confirmed with `arm-none-eabi-size`).

2. **Run under QEMU** (no hardware needed):

   ```bash
   qemu-system-arm -cpu cortex-m4 -machine lm3s6965evb -nographic \
       -kernel target/thumbv7em-none-eabihf/release/rust_app
   ```

   The firmware calls `c_add(2, 3)` and `c_toggle_bits(0xF0F0F0F0)`,
   stashes the results in a `static`, and idles in a `wfi` loop forever —
   there's no serial/semihosting output wired up, so it runs silently
   (add the `cortex-m-semihosting` crate for `println!`-to-host debug
   output if you want to see something on stdout). Confirmed it boots
   clean: running it for 3 seconds under `-d guest_errors,unimp` (traps
   faults/bad memory accesses/unimplemented instructions) produced zero
   output, i.e. no crash, no hard fault, no invalid access — it reached
   the `wfi` loop and sat there as designed.

3. **Full verification actually performed:** built a debug (unstripped)
   binary (`cargo build`, no `--release`), booted it under
   `qemu-system-arm -s -S` (halted, gdbstub on `:1234`), attached
   `arm-none-eabi-gdb`, set a breakpoint just after the firmware writes
   its results, and read memory directly:

   ```
   (gdb) target remote :1234
   (gdb) break *0x386
   (gdb) continue
   Breakpoint 1, core::ptr::read_volatile<(i32, u32)> (...)
   (gdb) x/2xw 0x20000000
   0x20000000 <rust_app::main::RESULT>: 0x00000005  0x0f0f0f0f
   ```

   `0x00000005` = `c_add(2, 3)`, `0x0f0f0f0f` = `c_toggle_bits(0xF0F0F0F0)`
   (bitwise NOT) — both computed by genuine ARM Thumb machine code
   (compiled by `arm-none-eabi-gcc` from `mathlib.c`) executing on an
   emulated Cortex-M4, called from the Rust firmware's hand-written
   `Reset` → `main` → `extern "C"` FFI path. This confirms the RAM
   init in `Reset` (`.bss` zeroing / `.data` copy from `memory.x`'s
   layout), the vector table wiring, and the FFI call itself are all
   correct end to end, not just "compiles."

---

## 4. Minimizing binary size

Both `Cargo.toml`s use the same release profile:

```toml
[profile.release]
opt-level = "z"     # optimize for size over speed
lto = true           # whole-program inlining/dead-code elimination across crates
codegen-units = 1    # one codegen unit = better cross-function size optimization
panic = "abort"      # no unwinding tables/landing pads (no stack unwinding on panic)
strip = true          # strip symbols from the output artifact
```

Plus, structurally:

- `#![no_std]` — no allocator, no unwinding runtime, no OS abstraction
  layer to link in.
- No heap (`alloc` crate) used in either example — every value here is
  either a plain integer/struct or a `static`, so there's no allocator to
  pull in at all.
- Avoiding `core::fmt`-based formatting (`{:?}`, `write!`, etc.) matters
  a lot in practice — the formatting machinery pulls in a surprising
  amount of code even in `no_std`; neither example uses it.
- `--nmagic` in `rust_calls_c/rust_app/.cargo/config.toml` tells the
  linker not to page-align sections, which otherwise wastes flash space
  padding out to 4 KB/64 KB boundaries meant for OS-backed memory
  protection — irrelevant on a microcontroller with no MMU.

---

## 5. Rust vs C: which is actually smaller, and which is more complex?

The two demo binaries as built are **not** a fair size comparison against
each other — `c_calls_rust/c_app/app.exe` is a hosted Windows PE (46 KB,
almost all C-runtime/`printf`/PE-header overhead), while
`rust_calls_c/rust_app`'s ELF is a bare-metal ARM image (2 KB total) with
no OS underneath either language. The gap there is hosted-vs-bare-metal,
not Rust-vs-C.

To isolate the actual variable, I compiled *identical logic* for the
*same* target (`thumbv7em-none-eabihf`), same optimization level
(`-Os`/`opt-level=z`), no host runtime on either side:

| | C (`arm-none-eabi-gcc -Os`) | Rust (`opt-level=z`, `panic=abort`) |
|---|---|---|
| `add(a, b)` | 4 bytes (`add r0,r1; bx lr`) | 8 bytes (`push {r7,lr}; mov r7,sp; add r0,r1; pop {r7,pc}`) |
| `toggle(x)` (bitwise NOT) | 4 bytes | 8 bytes |

**C wins, by a fixed 2x on trivial leaf functions.** I chased the cause
rather than guessing: `--emit=llvm-ir` shows every Rust function carries
the LLVM attribute `"frame-pointer"="all"`, and neither `-C opt-level=z`,
`-C force-frame-pointers=no`, `-C force-unwind-tables=no`, nor
`-C lto=fat -C codegen-units=1` changes it. The reason: Rust's built-in
`thumbv7em-none-eabihf` target *spec* hard-codes `frame_pointer: Always`
— chosen upstream so embedded code can still produce a stack backtrace
via the frame-pointer chain even without full DWARF/`.ARM.exidx` unwind
tables (which this profile already strips via `panic = "abort"`). It's a
property of the target definition, not a per-compile choice, so no
stable per-crate flag can turn it off.

**The actual fix** requires a custom target-spec JSON with
`"frame-pointer": "none"`, compiled via `-Z build-std=core` — which
needs a **nightly** toolchain (not installed here; a further ~300 MB+
download) since `core`/`compiler_builtins` aren't distributed prebuilt
for custom targets. Not pursued in this repo — the payoff is 4 bytes per
non-inlined leaf function, which matters for a hand-counted 20-byte demo
but is noise against any real firmware's actual logic size.

**Complexity is the sharper difference, and it isn't really about the
FFI direction at all** — it's about which language ends up owning
program startup:

- `c_calls_rust` (Rust as a callee library, C hosted): trivial —
  `#[repr(C)]`/`extern "C"`/`#[no_mangle]`, an ordinary `cargo build`,
  link the `.a` into an existing C build. C's `crt0` already initializes
  RAM; Rust never touches it.
- `rust_calls_c` (Rust owns `main`, bare metal): substantially more —
  hand-written vector table + `Reset` handler doing `.bss`/`.data` init,
  a linker script (`memory.x`), a `build.rs` invoking a matching
  cross-compiler, and target/CPU/FPU flags kept in sync between `rustc`
  and `gcc`. A C-only bare-metal program needs the identical vector
  table and linker script — Rust just doesn't get it for free the way
  `cortex-m-rt` would normally provide, since that crate was
  deliberately not used here so the mechanism stays visible.

**Summary:** C produces smaller machine code for equivalent simple
functions (a real, measured, if small, effect); the complexity gap
between the two example directions is much larger, and it's driven by
hosted-vs-bare-metal ownership of startup, not by which language calls
which.
