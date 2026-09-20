/* Minimal linker script for a Cortex-M target (matches QEMU's lm3s6965evb
 * machine and many real Cortex-M3/M4 parts closely enough for this demo).
 * Adjust ORIGIN/LENGTH to match your actual chip's datasheet. */
MEMORY
{
    FLASH : ORIGIN = 0x00000000, LENGTH = 256K
    RAM   : ORIGIN = 0x20000000, LENGTH = 64K
}

SECTIONS
{
    /* Cortex-M expects the vector table at the base of flash:
     * word 0 = initial stack pointer, word 1 = reset handler address. */
    .vector_table ORIGIN(FLASH) :
    {
        LONG(ORIGIN(RAM) + LENGTH(RAM)); /* initial stack pointer = top of RAM */
        KEEP(*(.vector_table.reset_vector));
    } > FLASH

    .text :
    {
        *(.text .text.*);
    } > FLASH

    .rodata :
    {
        *(.rodata .rodata.*);
    } > FLASH

    .bss :
    {
        _sbss = .;
        *(.bss .bss.*);
        _ebss = .;
    } > RAM

    .data : AT(ADDR(.rodata) + SIZEOF(.rodata))
    {
        _sdata = .;
        *(.data .data.*);
        _edata = .;
    } > RAM

    _sidata = LOADADDR(.data);

    /DISCARD/ :
    {
        *(.ARM.exidx .ARM.exidx.*); /* unwind tables - unused, panic = abort */
    }
}
