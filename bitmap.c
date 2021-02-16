#include <stdio.h>
#include <stdlib.h>

#include "bitmap.h"

word_t *create_bitmap(int n)
{
    word_t *map;
    int words;
    words = WORD_OFFSET(n) + 1;
    map = malloc(words * sizeof(word_t));
    for (int i = 0 ; i < words ; i++) {
        map[i] = 0UL;
    }
    return map;
}

void delete_bitmap(word_t **map)
{
    if (*map) {
        free(*map);
        *map = NULL;
    }
}

void set_bit(word_t *bitmap, int n)
{
    /* no error-checking for now */
    bitmap[WORD_OFFSET(n)] |= (1UL << BIT_OFFSET(n));
}

void clear_bit(word_t *bitmap, int n)
{
    /* no error checking for now */
    bitmap[WORD_OFFSET(n)] &= ~(1UL << BIT_OFFSET(n));
}

int test_bit(word_t *bitmap, int n)
{
    word_t word;
    word = bitmap[WORD_OFFSET(n)] & (1UL << BIT_OFFSET(n));
    return word != 0;
}
