/*
 * Copyright 2020 by Heiko Schäfer <heiko@rangun.de>
 *
 * This file is part of DiskFit.
 *
 * DiskFit is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 3 of
 * the License, or (at your option) any later version.
 *
 * DiskFit is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with DiskFit.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <assert.h>
#include <string.h>
#include <stdlib.h>
#include <pthread.h>

#ifndef NDEBUG
#include <stdio.h>
#endif

#include "blocking_queue.h"

struct blocking_queue_t {
    pthread_mutex_t lock;
    pthread_cond_t notFull;
    pthread_cond_t notEmpty;

    size_t capacity;
    size_t front;
    size_t rear;
    size_t size;

    size_t elem_size;
    void  *entries;
};

static DISKFIT_ALLOC _bq_mem_alloc = malloc;
static DISKFIT_FREE  _bq_mem_free  = free;

void blocking_queue_take(struct blocking_queue_t *q, void *out) {

    assert(q);

    pthread_mutex_lock(&(q->lock));

    while(q->size == 0u) pthread_cond_wait(&(q->notEmpty), &(q->lock));

    __builtin_memcpy(out, (q->entries + (q->front * q->elem_size)), q->elem_size);
    q->front = (q->front + 1u) % q->capacity;
    --q->size;

    pthread_cond_broadcast(&(q->notFull));
    pthread_mutex_unlock(&(q->lock));
}

void blocking_queue_put(struct blocking_queue_t *q, DATA dataFn, void *user_data) {

    assert(q);

    pthread_mutex_lock(&(q->lock));

    if(q->size == q->capacity) pthread_cond_wait(&(q->notFull), &(q->lock));

    q->rear = (q->rear + 1u) % q->capacity;
    dataFn((q->entries + (q->rear * q->elem_size)), q->elem_size, user_data);
    ++q->size;

    pthread_cond_broadcast(&(q->notEmpty));
    pthread_mutex_unlock(&(q->lock));
}

struct blocking_queue_t *blocking_queue_create(size_t size, size_t capacity) {

#ifndef NDEBUG
    fprintf(stderr, "[DEBUG] blocking queue capacity: %zu\n", capacity);
#endif

    struct blocking_queue_t *q =
        (struct blocking_queue_t *)_bq_mem_alloc(sizeof(struct blocking_queue_t));

    pthread_mutex_init(&(q->lock), NULL);
    pthread_cond_init(&(q->notFull), NULL);
    pthread_cond_init(&(q->notEmpty), NULL);

    q->capacity = capacity;
    q->front = q->size = 0u;
    q->rear = capacity - 1u;
    q->elem_size = size;
    q->entries = _bq_mem_alloc(size * capacity);

    if(q->entries) {
        return q;
    } else {
        _bq_mem_free((void *)q);
        q = NULL;
    }

    assert(q == NULL);
    return NULL;
}

void blocking_queue_destroy(struct blocking_queue_t * const q) {

    if(q) {

        pthread_cond_destroy(&(q->notEmpty));
        pthread_cond_destroy(&(q->notFull));
        pthread_mutex_destroy(&(q->lock));

        _bq_mem_free((void *)q->entries);
    }

    _bq_mem_free((void *)q);
}

void blocking_queue_set_mem_funcs(DISKFIT_ALLOC a, DISKFIT_FREE f) {
    _bq_mem_alloc = a ? a : malloc;
    _bq_mem_free  = f ? f : free;
}

// kate: indent-mode cstyle; indent-width 4; replace-tabs on; remove-trailing-space on;
