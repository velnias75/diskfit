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

#ifndef BLOCKING_QUEUE_H
#define BLOCKING_QUEUE_H

#include "diskfit.h"

#ifdef _cplusplus
extern "C" {
#endif

typedef struct blocking_queue_t blocking_queue_t;
typedef void (*DATA)(void *, size_t, void *);

blocking_queue_t *blocking_queue_create(size_t, size_t);
void blocking_queue_destroy(blocking_queue_t * const);

void blocking_queue_put(blocking_queue_t *, DATA, void *);
void blocking_queue_take(blocking_queue_t *, void *);

size_t blocking_queue_elem_size(blocking_queue_t *);
void blocking_queue_set_mem_funcs(DISKFIT_ALLOC a, DISKFIT_FREE f);

#ifdef _cplusplus
}
#endif

#endif /* BLOCKING_QUEUE_H */

// kate: indent-mode cstyle; indent-width 4; replace-tabs on; remove-trailing-space on;
