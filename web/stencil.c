__attribute__((export_name("stencil"))) void stencil(const double *x, double *y, int nx, int ny) {
 for(int j=0;j<ny;j++) for(int i=0;i<nx;i++){int k=j*nx+i; y[k]=4*x[k]-(i?x[k-1]:0)-(i+1<nx?x[k+1]:0)-(j?x[k-nx]:0)-(j+1<ny?x[k+nx]:0);}
}
