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

#include <stdlib.h>
#include <pthread.h>

#include "blocking_queue.h"

struct blocking_queue_t {
    pthread_mutex_t lock;
    pthread_cond_t notFull;
    pthread_cond_t notEmpty;

    size_t capacity;
    size_t count;
    size_t read;
    size_t write;

    const void **entries;
};

const void *blocking_queue_take(struct blocking_queue_t *q) {

    pthread_mutex_lock(&(q->lock));

    while(blocking_queue_isEmpty(q)) {
        pthread_cond_wait(&(q->notEmpty), &(q->lock));
    }

    const void *e = q ? q->entries[(q->read)++] : NULL;

    if(q->read == q->capacity) q->read = 0u;

    --q->count;

    pthread_cond_broadcast(&(q->notFull));
    pthread_mutex_unlock(&(q->lock));

    return e;
}

void blocking_queue_put(struct blocking_queue_t *q, const void * const e) {

    pthread_mutex_lock(&(q->lock));

    if(q) {

        if(q->count == q->capacity) {
            pthread_cond_wait(&(q->notFull), &(q->lock));
        }

        q->entries[(q->write)++] = e;

        if(q->write == q->capacity) q->write = 0u;

        ++q->count;

        pthread_cond_broadcast(&(q->notEmpty));
    }

    pthread_mutex_unlock(&(q->lock));
}

inline int blocking_queue_isEmpty(struct blocking_queue_t *q) {
    return q ? q->count == 0u : 1;
}

struct blocking_queue_t *blocking_queue_create(size_t capacity) {

    struct blocking_queue_t *q =
        (struct blocking_queue_t *)malloc(sizeof(struct blocking_queue_t));

    pthread_mutex_init(&(q->lock), NULL);
    pthread_cond_init(&(q->notFull), NULL);
    pthread_cond_init(&(q->notEmpty), NULL);

    q->capacity = capacity;
    q->count = q->read = q->write = 0u;
    q->entries = calloc(sizeof(void *), capacity);

    if(q->entries) {
        return q;
    } else {
        free((void *)q);
    }

    return NULL;
}

void blocking_queue_destroy(struct blocking_queue_t * const q) {

    if(q) {
        pthread_cond_destroy(&(q->notEmpty));
        pthread_cond_destroy(&(q->notFull));
        pthread_mutex_destroy(&(q->lock));
        free((void *)q->entries);
    }

    free((void *)q);
}

// kate: indent-mode cstyle; indent-width 4; replace-tabs on; remove-trailing-space on;
