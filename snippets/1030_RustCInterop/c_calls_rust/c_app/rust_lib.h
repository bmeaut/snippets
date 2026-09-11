/* Hand-written header for rust_lib (see ../rust_lib/src/lib.rs).
 * In a real project, generate this with `cbindgen` instead of writing it
 * by hand, so it can never drift out of sync with the Rust definitions. */
#ifndef RUST_LIB_H
#define RUST_LIB_H

#include <stdint.h>
#include <stddef.h>

typedef struct {
    int32_t x;
    int32_t y;
} Point;

int32_t rust_add(int32_t a, int32_t b);
int64_t rust_point_distance_sq(Point p);
uint32_t rust_sum_bytes(const uint8_t *data, size_t len);

#endif /* RUST_LIB_H */
