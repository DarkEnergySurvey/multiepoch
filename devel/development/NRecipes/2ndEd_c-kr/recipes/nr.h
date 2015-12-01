/* CAUTION: This is the traditional K&R C (only) version of the Numerical
   Recipes utility file nr.h.  Do not confuse this file with the
   same-named file nr.h that is supplied in the 'misc' subdirectory.
   *That* file is the one from the book, and contains both ANSI and
   traditional K&R versions, along with #ifdef macros to select the
   correct version.  *This* file contains only traditional K&R.           */

#ifndef _NR_H_
#define _NR_H_

#ifndef _FCOMPLEX_DECLARE_T_
typedef struct FCOMPLEX {float r,i;} fcomplex;
#define _FCOMPLEX_DECLARE_T_
#endif /* _FCOMPLEX_DECLARE_T_ */

#ifndef _ARITHCODE_DECLARE_T_
typedef struct {
	unsigned long *ilob,*iupb,*ncumfq,jdif,nc,minint,nch,ncum,nrad;
} arithcode;
#define _ARITHCODE_DECLARE_T_
#endif /* _ARITHCODE_DECLARE_T_ */

#ifndef _HUFFCODE_DECLARE_T_
typedef struct {
	unsigned long *icod,*ncod,*left,*right,nch,nodemax;
} huffcode;
#define _HUFFCODE_DECLARE_T_
#endif /* _HUFFCODE_DECLARE_T_ */

void addint();
void airy();
void amebsa();
void amoeba();
float amotry();
float amotsa();
void anneal();
double anorm2();
void arcmak();
void arcode();
void arcsum();
void asolve();
void atimes();
void avevar();
void balanc();
void banbks();
void bandec();
void banmul();
void bcucof();
void bcuint();
void beschb();
float bessi();
float bessi0();
float bessi1();
void bessik();
float bessj();
float bessj0();
float bessj1();
void bessjy();
float bessk();
float bessk0();
float bessk1();
float bessy();
float bessy0();
float bessy1();
float beta();
float betacf();
float betai();
float bico();
void bksub();
float bnldev();
float brent();
void broydn();
void bsstep();
void caldat();
void chder();
float chebev();
void chebft();
void chebpc();
void chint();
float chixy();
void choldc();
void cholsl();
void chsone();
void chstwo();
void cisi();
void cntab1();
void cntab2();
void convlv();
void copy();
void correl();
void cosft();
void cosft1();
void cosft2();
void covsrt();
void crank();
void cyclic();
void daub4();
float dawson();
float dbrent();
void ddpoly();
int decchk();
void derivs();
float df1dim();
void dfour1();
void dfpmin();
float dfridr();
void dftcor();
void dftint();
void difeq();
void dlinmin();
double dpythag();
void drealft();
void dsprsax();
void dsprstx();
void dsvbksb();
void dsvdcmp();
void eclass();
void eclazz();
float ei();
void eigsrt();
float elle();
float ellf();
float ellpi();
void elmhes();
float erfcc();
float erff();
float erffc();
void eulsum();
float evlmem();
float expdev();
float expint();
float f1();
float f1dim();
float f2();
float f3();
float factln();
float factrl();
void fasper();
void fdjac();
void fgauss();
void fill0();
void fit();
void fitexy();
void fixrts();
void fleg();
void flmoon();
float fmin();
void four1();
void fourew();
void fourfs();
void fourn();
void fpoly();
void fred2();
float fredin();
void frenel();
void frprmn();
void ftest();
float gamdev();
float gammln();
float gammp();
float gammq();
float gasdev();
void gaucof();
void gauher();
void gaujac();
void gaulag();
void gauleg();
void gaussj();
void gcf();
float golden();
void gser();
void hpsel();
void hpsort();
void hqr();
void hufapp();
void hufdec();
void hufenc();
void hufmak();
void hunt();
void hypdrv();
fcomplex hypgeo();
void hypser();
unsigned short icrc();
unsigned short icrc1();
unsigned long igray();
void iindexx();
void indexx();
void interp();
int irbit1();
int irbit2();
void jacobi();
void jacobn();
long julday();
void kendl1();
void kendl2();
void kermom();
void ks2d1s();
void ks2d2s();
void ksone();
void kstwo();
void laguer();
void lfit();
void linbcg();
void linmin();
void lnsrch();
void load();
void load1();
void load2();
void locate();
void lop();
void lubksb();
void ludcmp();
void machar();
void matadd();
void matsub();
void medfit();
void memcof();
int metrop();
void mgfas();
void mglin();
float midexp();
float midinf();
float midpnt();
float midsql();
float midsqu();
void miser();
void mmid();
void mnbrak();
void mnewt();
void moment();
void mp2dfr();
void mpadd();
void mpdiv();
void mpinv();
void mplsh();
void mpmov();
void mpmul();
void mpneg();
void mppi();
void mprove();
void mpsad();
void mpsdv();
void mpsmu();
void mpsqrt();
void mpsub();
void mrqcof();
void mrqmin();
void newt();
void odeint();
void orthog();
void pade();
void pccheb();
void pcshft();
void pearsn();
void period();
void piksr2();
void piksrt();
void pinvs();
float plgndr();
float poidev();
void polcoe();
void polcof();
void poldiv();
void polin2();
void polint();
void powell();
void predic();
float probks();
void psdes();
void pwt();
void pwtset();
float pythag();
void pzextr();
float qgaus();
void qrdcmp();
float qromb();
float qromo();
void qroot();
void qrsolv();
void qrupdt();
float qsimp();
float qtrap();
float quad3d();
void quadct();
void quadmx();
void quadvl();
float ran0();
float ran1();
float ran2();
float ran3();
float ran4();
void rank();
void ranpt();
void ratint();
void ratlsq();
double ratval();
float rc();
float rd();
void realft();
void rebin();
void red();
void relax();
void relax2();
void resid();
float revcst();
void reverse();
float rf();
float rj();
void rk4();
void rkck();
void rkdumb();
void rkqs();
void rlft3();
float rofunc();
void rotate();
void rsolv();
void rstrct();
float rtbis();
float rtflsp();
float rtnewt();
float rtsafe();
float rtsec();
void rzextr();
void savgol();
void score();
void scrsho();
float select();
float selip();
void shell();
void shoot();
void shootf();
void simp1();
void simp2();
void simp3();
void simplx();
void simpr();
void sinft();
void slvsm2();
void slvsml();
void sncndn();
double snrm();
void sobseq();
void solvde();
void sor();
void sort();
void sort2();
void sort3();
void spctrm();
void spear();
void sphbes();
void splie2();
void splin2();
void spline();
void splint();
void spread();
void sprsax();
void sprsin();
void sprspm();
void sprstm();
void sprstp();
void sprstx();
void stifbs();
void stiff();
void stoerm();
void svbksb();
void svdcmp();
void svdfit();
void svdvar();
void toeplz();
void tptest();
void tqli();
float trapzd();
void tred2();
void tridag();
float trncst();
void trnspt();
void ttest();
void tutest();
void twofft();
void vander();
void vegas();
void voltra();
void wt1();
void wtn();
void wwghts();
int zbrac();
void zbrak();
float zbrent();
void zrhqr();
float zriddr();
void zroots();

#endif /* _NR_H_ */