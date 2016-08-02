/*
 * Copyright 2016 by Heiko Schäfer <heiko@rangun.de>
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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <math.h>

#include <wordexp.h>
#include <libgen.h>

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

typedef struct {
  char *fname;
  off_t fsize;
} FITEM;

typedef struct {
  FITEM *entries;
  size_t size;
  off_t total;
} FITEMLIST;

typedef void (*ADDFUN)(FITEM *array, int len, off_t total);

FITEMLIST *CANDIDATES = NULL;
size_t CANDIDATES_NUM = 0;

off_t target_size(const char *tgs) {
  
  char suff = '\0';
  double fac = 1.0;
  
  if(!strncasecmp(tgs, "dvd", 3)) return 4707319808L;
  if(!strncasecmp(tgs, "cd", 2)) return 734003200L;
  
  double b = 0.0;
  
  sscanf(tgs, "%lf%c", &b, &suff);
  
  switch(suff) {
    case 'G':
    case 'g':
      fac = 1073741824L;
      break;
    case 'M':
    case 'm':
      fac = 1048576L;
      break;
    case 'K':
    case 'k':
      fac = 1024L;
      break;
  }
  
  return b * fac;
}

off_t sum(const FITEM *item, int n) {
  
  int i;
  off_t sum = 0;
  
  for(i = 0; i < n; ++i) sum += item[i].fsize;
  
  return sum;
}

void swap(FITEM *a, FITEM *b) {
 
  if(a != b) {
    FITEM h;
    
    memcpy(&h, b, sizeof(FITEM));
    memcpy(b,  a, sizeof(FITEM));
    memcpy(a, &h, sizeof(FITEM));
  }
}

void permute(FITEM *array, int i, int length, off_t target, ADDFUN adder) { 
  
  if(length == i) {
    
    int k = length - 1;
    off_t s = 0;
    
    while(k >= 0 && (s = sum(array, k + 1)) > target) --k;
    
    if(s <= target) adder(array, k + 1, s);
    
    return;
  }
  
  int j = i;
  
  for(j = i; j < length; ++j) { 
    swap(array + i, array + j);
    permute(array, i + 1, length, target, adder);
    swap(array + i, array + j);
  }
  
  return;
}

int fitem_cmp(const void *a, const void *b) {
  return strcmp(((FITEM *)a)->fname, ((FITEM *)b)->fname);
}

void addCandidate(FITEM *array, int len, off_t total) {
  
  if(total == 0) return;
  
  int i;
  
  FITEMLIST l = { malloc(len * sizeof(FITEM)), len, total };
  
  for(i = 0; i < len; ++i) {
    memcpy(&(l.entries[i]), &(array[i]), sizeof(FITEM));
  }
  
  qsort(l.entries, l.size, sizeof(FITEM), fitem_cmp);
  
  if(!CANDIDATES) {
    CANDIDATES = malloc(sizeof(FITEMLIST));
  } else {
    
    size_t j, k;
    
    for(j = 0; j < CANDIDATES_NUM; ++j) {
      
      if(CANDIDATES[j].size == l.size && CANDIDATES[j].total == l.total) {

	int dup = 0;

	for(k = 0; k < l.size; ++k) {
	  dup |= (CANDIDATES[j].entries[k].fsize == l.entries[k].fsize && 
	  !strcmp(CANDIDATES[j].entries[k].fname, l.entries[k].fname));
	}

	if(dup) {
	  free(l.entries);
	  return;
	}
      }
    }
    
    CANDIDATES = realloc(CANDIDATES, (CANDIDATES_NUM + 1) * sizeof(FITEMLIST));
  }
  
  memcpy(&(CANDIDATES[CANDIDATES_NUM]), &l, sizeof(FITEMLIST));
  
  ++CANDIDATES_NUM;
}

const char *hrsize(off_t s) {
  
  char *r = malloc(1024 * sizeof(char));
  const double d = log(s)/M_LN2;
  
  if(d >= 30.0) {
    snprintf(r, 1023, "%.2f GByte", (float)s/1073741824.0f);
  } else if(d >= 20.0) {
    snprintf(r, 1023, "%.2f MByte", (float)s/1048576.0f);
  } else if(d >= 10.0) {
    snprintf(r, 1023, "%.2f KByte", (float)s/1024.0f);
  } else {
    snprintf(r, 1023, "%ld Byte", s);
  }
  
  return r;
}

int cand_cmp(const void *a, const void *b) {
  
  if(((FITEMLIST *)a)->total < ((FITEMLIST *)b)->total) return -1;
  if(((FITEMLIST *)a)->total > ((FITEMLIST *)b)->total) return 1;
  
  return 0;
}

int main(int argc, char *argv[]) {
  
  fprintf(stderr, PACKAGE_STRING " - (c) 2016 by Heiko Schaefer <heiko@rangun.de>\n");
  
  if(argc < 3) {
    
    fprintf(stdout, "Usage: %s (cd|dvd|target_size[G|M|K]) file_pattern...\n\n", argv[0]);
    fprintf(stdout, "Set environment variable DISKFIT_STRIPDIR to any value to strip directories.\n");
    
    return EXIT_FAILURE;
    
  } else {
    
    size_t j;
    int i, nitems = 0;
    FITEM *fitems = NULL;
    off_t tsize = 0;
    const off_t tg = target_size(argc > 1 ? argv[1] : "dvd");
    const char *hr_tot, *hr_tg;
    wordexp_t p;
    
    memset(&p, 0, sizeof(wordexp_t));
    
    for(i = 0; i < argc - 2; ++i) 
      wordexp(argv[i+2], &p, WRDE_NOCMD|WRDE_APPEND);
    
    fitems = malloc(p.we_wordc * sizeof(FITEM));
    
    for(j = 0; j < p.we_wordc; ++j) {
      
      struct stat st;
      
      if(!stat(p.we_wordv[j], &st)) {

	tsize += st.st_size;

	fitems[j].fname = p.we_wordv[j];
	fitems[j].fsize = st.st_size;

	++nitems;
      }
    }
    
    permute(fitems, 0, nitems, tg, addCandidate);
    qsort(CANDIDATES, CANDIDATES_NUM, sizeof(FITEMLIST), cand_cmp);
    
    const int stripdir = getenv("DISKFIT_STRIPDIR") != NULL;
    
    for(j = 0; j < CANDIDATES_NUM; ++j) {
      
      const char *hrs;
      size_t l;
      
      fprintf(stdout, "[ ");
      
      for(l = 0; l < CANDIDATES[j].size; ++l) {
	
	char *bc = stripdir ? strdup(CANDIDATES[j].entries[l].fname) : CANDIDATES[j].entries[l].fname;
	
	fprintf(stdout, "'%s' ", stripdir ? basename(bc) : bc);
	
	if(stripdir) free(bc);
      }
      
      fprintf(stdout, "] = %s\n", (hrs = hrsize(CANDIDATES[j].total)));
      
      free((void *)hrs);
      free(CANDIDATES[j].entries);
    }
    
    free(fitems);
    free(CANDIDATES);
    
    wordfree(&p);
    
    fprintf(stderr, "Total size: %s - Target size: %s\n", 
	    (hr_tot = hrsize(tsize)), (hr_tg = hrsize(tg)));
    
    free((void *)hr_tot);
    free((void *)hr_tg);
  }
  
  return EXIT_SUCCESS;
}
