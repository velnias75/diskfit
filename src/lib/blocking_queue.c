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
    size_t pos;
    void **entries;
};

void *blocking_queue_take(struct blocking_queue_t *q) {

    pthread_mutex_lock(&(q->lock));

    while(blocking_queue_isEmpty(q)) {
        pthread_cond_wait(&(q->notEmpty), &(q->lock));
    }

    void *e = q ? q->entries[--q->pos] : NULL;

    pthread_cond_broadcast(&(q->notFull));
    pthread_mutex_unlock(&(q->lock));

    return e;
}

void blocking_queue_put(struct blocking_queue_t *q, void * const e) {

    pthread_mutex_lock(&(q->lock));

    if(q) {

        if(!((q->pos + 1u) <= q->capacity)) {
            pthread_cond_wait(&(q->notFull), &(q->lock));
        }

        q->entries[(q->pos)++] = e;
        pthread_cond_broadcast(&(q->notEmpty));
    }

    pthread_mutex_unlock(&(q->lock));
}

int blocking_queue_isEmpty(struct blocking_queue_t *q) {

    pthread_mutex_lock(&(q->lock));

    const int ret = q ? q->pos == 0 : 1;

    pthread_mutex_unlock(&(q->lock));

    return ret;
}

struct blocking_queue_t *blocking_queue_create(size_t n) {

    struct blocking_queue_t *q =
        (struct blocking_queue_t *)malloc(sizeof(struct blocking_queue_t));

    pthread_mutex_init(&(q->lock), NULL);
    pthread_cond_init(&(q->notFull), NULL);
    pthread_cond_init(&(q->notEmpty), NULL);

    q->capacity = n;
    q->pos = 0u;
    q->entries = calloc(sizeof(void *), n);

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
