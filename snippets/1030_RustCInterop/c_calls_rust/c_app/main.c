#include <stdio.h>
#include "rust_lib.h"

int main(void) {
    int32_t sum = rust_add(2, 3);
    printf("rust_add(2, 3)            = %d\n", sum);

    Point p = { .x = 3, .y = 4 };
    int64_t d2 = rust_point_distance_sq(p);
    printf("rust_point_distance_sq(p) = %lld\n", (long long)d2);

    uint8_t bytes[] = { 1, 2, 3, 4, 5 };
    uint32_t total = rust_sum_bytes(bytes, sizeof(bytes));
    printf("rust_sum_bytes(bytes)     = %u\n", total);

    return 0;
}
