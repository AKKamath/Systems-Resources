#ifndef BITMAP_H_
#define BITMAP_H_

#include <stdint.h>
#include <inttypes.h>
#include <limits.h>

typedef uint64_t word_t;

enum {
    BITS_PER_WORD = sizeof(word_t) * CHAR_BIT,
    CHARS_PER_WORD = sizeof(word_t) / sizeof(char)
};
#define WORD_OFFSET(n) ((n) / BITS_PER_WORD)
#define BIT_OFFSET(n) ((n) % BITS_PER_WORD)

word_t *create_bitmap(int n);
void delete_bitmap(word_t **map);
void set_bit(word_t *bitmap, int n);
void clear_bit(word_t *bitmap, int n);
int test_bit(word_t *bitmap, int n);

#endif
