#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

typedef struct {
  char *fname;
  off_t fsize;
} FITEM;

off_t sum(FITEM *item, int n) {
  
  int i;
  off_t sum = 0;
  
  for(i = 0; i < n; ++i) sum += item[i].fsize;
  
  return sum;
}

void swap(FITEM *a, FITEM *b) {
  
  FITEM h = { b->fname, b->fsize };

  b->fname = a->fname;
  b->fsize = a->fsize;
  
  a->fname = h.fname;
  a->fsize = h.fsize;
}

void permute(FITEM *array, int i, int length, off_t target) { 
  
  int l, k = length - 1;
  off_t s = 0;
  
  if(length == i) {
    
    while(k >= 0 && (s = sum(array, k + 1)) > target) --k;
    
    if(s <= target) {
      fprintf(stdout, "[ ");
      for(l = 0; l < k + 1; ++l) fprintf(stdout, "'%s' ", array[l].fname);
      fprintf(stdout, "] = %.2f GByte\n", (float)s/1073741824.0f);
    }
    
    return;
  }
  
  int j = i;
  
  for(j = i; j < length; ++j) { 
    swap(array + i, array + j);
    permute(array, i + 1, length, target);
    swap(array + i, array + j);
  }
  
  return;
}

int main(int argc, char *argv[]) {
  
  int i, nitems = 0;
  FITEM *fitems = NULL;
  off_t tsize = 0, tg = atol(argv[1]);
  struct stat st;
  
  fprintf(stderr, "DiskFit - (c) 2016 by Heiko Schaefer <heiko@rangun.de>\n");
  
  if(argc < 3) {
    
    fprintf(stderr, "Usage: %s target_size files...\n", argv[0]);
    return EXIT_FAILURE;
    
  } else {
    
    tg = tg == 0 ? 4724464025 : tg;
    
    fitems = calloc(argc - 2, sizeof(FITEM));
    
    for(i = 0; i < argc - 2; ++i) {
      
      if(!stat(argv[i+2], &st)) {
	
	tsize += st.st_size;
      
	fitems[nitems].fname = argv[i+2];
	fitems[nitems].fsize = st.st_size;
	
	++nitems;
	
      }
    }
    
    permute(fitems, 0, nitems, tg);
    
    free(fitems);
    
    fprintf(stderr, "Total size: %.2f GByte - Target size: %.2f GByte\n", 
	    ((float)tsize)/1073741824.0f, (float)tg/1073741824.0f);
  }
  
  return EXIT_SUCCESS;
}