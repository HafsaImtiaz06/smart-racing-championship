#ifndef TRACKGEN_H
#define TRACKGEN_H
#include <iostream>
#include "../planning/refuel.h"

// pipeline: random vertices -> candidate roads -> Kruskal MST -> extra roads (cycles/shortcuts/one-way)
// -> backtracking placement (finish, checkpoints, stations, pickups) -> obstacle backtracking -> validator
// fuel unit = tenths. cap 1000 = 100 units, maxbuy 400 = 40 units. edge fuel = len/2 * (9+diff)/10

const int gv=64, ge=gv*(gv-1)/2;
struct gedge{int u,v,len,diff,fuel,sc,dir,mst,obs;};
struct gparam{int n,k,f,p,nobs,nshort,nextra,noneway,radius,maxlen,maxdeg,sgap,maxtries,maxnodes;};
const int gcap=1000, gbuy=400, gstime=30;

static gedge ce[ge], te[ge];
static int nce,nte;
static int tx[gv],ty[gv],ttyp[gv],tord[gv],tdeg[gv],hopm[gv][gv];
static int tn,tstart,tfin;
static unsigned rs;
static gparam gp;
long long gnodes=0, gobsn=0;
int gprune[8];
// types: 0 intersection,1 start,2 finish,3 checkpoint,4 fuel,5 nitro,6 dead end

int rnd(int m){ rs=rs*1664525u+1013904223u; return (int)((rs>>8)%(unsigned)m); }
int isqrt(int a){ int r=0; while((r+1)*(r+1)<=a) r++; return r; }
int efuel(const gedge& e){ int f=e.fuel*(9+e.diff)/10; return f; }

bool (*cmpf)(int,int);
void sift(int* a,int i,int n){
    for(;;){
        int l=2*i+1,r=l+1,m=i;
        if(l<n && cmpf(a[m],a[l])) m=l;
        if(r<n && cmpf(a[m],a[r])) m=r;
        if(m==i) return;
        int t=a[i]; a[i]=a[m]; a[m]=t; i=m;
    }
}
void hsort(int* a,int n,bool (*f)(int,int)){
    cmpf=f;
    for(int i=n/2-1;i>=0;i--) sift(a,i,n);
    for(int i=n-1;i>0;i--){ int t=a[0]; a[0]=a[i]; a[i]=t; sift(a,0,i); }
}
bool clen(int a,int b){ if(ce[a].len!=ce[b].len) return ce[a].len<ce[b].len; return a<b; }
static int hopv[ge];
bool chop(int a,int b){
    if(hopv[a]!=hopv[b]) return hopv[a]>hopv[b];
    if(ce[a].len!=ce[b].len) return ce[a].len<ce[b].len;
    return a<b;
}

static int dsu[gv];
int fnd(int x){ while(dsu[x]!=x){ dsu[x]=dsu[dsu[x]]; x=dsu[x]; } return x; }

void addedge(int u,int v,int len,int sc,int dir,int mst){
    gedge& e=te[nte++];
    e.u=u; e.v=v; e.len=len; e.sc=sc; e.dir=dir; e.mst=mst; e.obs=0;
    e.diff=sc?3+rnd(3):1+rnd(5);
    e.fuel=len/2; if(e.fuel<1) e.fuel=1;
    tdeg[u]++; tdeg[v]++;
}

static int qv[gv],bd[gv],pvv[gv],pee[gv];
int bfsp(int s,int t,int skip,int undirected){
    for(int i=0;i<tn;i++) bd[i]=-1;
    int qh=0,qt=0; bd[s]=0; qv[qt++]=s;
    while(qh<qt){
        int x=qv[qh++];
        for(int i=0;i<nte;i++){
            if(i==skip) continue;
            gedge& e=te[i]; int y=-1;
            if(e.u==x) y=e.v; else if((undirected||!e.dir) && e.v==x) y=e.u;
            if(y<0||bd[y]>=0) continue;
            bd[y]=bd[x]+1; pvv[y]=x; pee[y]=i; qv[qt++]=y;
        }
    }
    return t>=0?bd[t]:qt;
}
void calchop(){
    for(int s=0;s<tn;s++){
        bfsp(s,-1,-1,1);
        for(int t=0;t<tn;t++) hopm[s][t]=bd[t]<0?99:bd[t];
    }
}

// min-fuel directed path s->t, appends to route arrays
static int rv[512],re[512],nrv;
int mfleg(int s,int t){
    int dist[gv],par[gv],pe2[gv]; bool dn[gv];
    for(int i=0;i<tn;i++){ dist[i]=rinf; dn[i]=false; }
    dist[s]=0;
    for(int it=0;it<tn;it++){
        int x=-1;
        for(int i=0;i<tn;i++) if(!dn[i] && dist[i]<rinf && (x<0||dist[i]<dist[x])) x=i;
        if(x<0) break;
        dn[x]=true;
        for(int i=0;i<nte;i++){
            gedge& e=te[i]; int y=-1;
            if(e.u==x) y=e.v; else if(!e.dir && e.v==x) y=e.u;
            if(y<0) continue;
            int w=efuel(e);
            if(dist[x]+w<dist[y]){ dist[y]=dist[x]+w; par[y]=x; pe2[y]=i; }
        }
    }
    if(dist[t]>=rinf) return -1;
    int tv[gv],tee[gv],c=0,x=t;
    while(x!=s){ tv[c]=x; tee[c]=pe2[x]; c++; x=par[x]; }
    for(int i=c-1;i>=0;i--){ rv[nrv]=tv[i]; re[nrv-1]=tee[i]; nrv++; }
    return dist[t];
}

// placement slots
static int skind[gv],sidx[gv],sv[gv],cpv[gv],ns,soff;
int okslot(int s,int v){
    if(ttyp[v]!=0) return 1;
    if(tdeg[v]<2) return 2;
    int kd=skind[s];
    if(kd==2){ if(hopm[tstart][v]<3) return 3; }
    else if(kd==3){ int p=(sidx[s]==1)?tstart:cpv[sidx[s]-1]; if(hopm[p][v]<2) return 3; }
    else if(kd==4){ for(int q=0;q<s;q++) if(skind[q]==4 && hopm[sv[q]][v]<gp.sgap) return 4; }
    else if(kd==5){ for(int q=0;q<s;q++) if(skind[q]==5 && hopm[sv[q]][v]<2) return 5; }
    return 0;
}
bool place(int s){
    if(s==ns) return true;
    for(int i=0;i<tn;i++){
        int v=(i+soff)%tn;
        if(gnodes>=gp.maxnodes) return false;
        gnodes++;
        int r=okslot(s,v);
        if(r){ gprune[r]++; continue; }
        ttyp[v]=skind[s]; sv[s]=v;
        if(skind[s]==3){ cpv[sidx[s]]=v; tord[v]=sidx[s]; }
        if(place(s+1)) return true;
        ttyp[v]=0; tord[v]=0;
    }
    return false;
}

static bool isbr[ge]; static int ovu[gv];
bool placeobs(int k,int from){
    if(k==gp.nobs) return true;
    for(int i=from;i<nte;i++){
        if(++gobsn>gp.maxnodes) return false;
        gedge& e=te[i];
        if(e.sc||isbr[i]){ gprune[6]++; continue; }
        if(e.u==tstart||e.v==tstart||e.u==tfin||e.v==tfin||ovu[e.u]||ovu[e.v]){ gprune[7]++; continue; }
        int od=e.diff; e.obs=1; e.diff=5; ovu[e.u]=ovu[e.v]=1;
        if(placeobs(k+1,i+1)) return true;
        e.obs=0; e.diff=od; ovu[e.u]=ovu[e.v]=0;
    }
    return false;
}

const char* vmsg[]={"ok","candidate graph disconnected (forest, not spanning tree)",
 "placement failed (no slot fits / node limit)","no cycle","fewer than 2 shortcuts","no dead end",
 "ordered checkpoints unreachable in directed graph","no alternative start-finish route","no feasible fuel plan"};

int validate(){
    if(bfsp(0,-1,-1,1)!=tn) return 1;
    int c=0; for(int i=0;i<tn;i++) if(ttyp[i]==3) c++;
    if(c!=gp.k) return 2;
    if(nte<tn) return 3;
    int s=0; for(int i=0;i<nte;i++) if(te[i].sc) s++;
    if(s<2) return 4;
    int d=0; for(int i=0;i<tn;i++) if(ttyp[i]==6) d++;
    if(!d) return 5;
    int cur=tstart;
    for(int o=1;o<=gp.k;o++){ if(bfsp(cur,cpv[o],-1,0)<0) return 6; cur=cpv[o]; }
    if(bfsp(cur,tfin,-1,0)<0) return 6;
    if(bfsp(tfin,tstart,-1,0)<0) return 6;
    if(bfsp(tstart,tfin,-1,0)<0) return 6;
    int pl[gv],pc=0,x=tfin;
    while(x!=tstart){ pl[pc++]=pee[x]; x=pvv[x]; }
    bool alt=false;
    for(int i=0;i<pc;i++) if(bfsp(tstart,tfin,pl[i],0)>=0) alt=true;
    if(!alt) return 7;
    nrv=1; rv[0]=tstart; cur=tstart;
    for(int o=1;o<=gp.k;o++){ if(mfleg(cur,cpv[o])<0) return 8; cur=cpv[o]; }
    if(mfleg(cur,tfin)<0) return 8;
    int sidxs[rmaxm+1],m=1; sidxs[0]=0;
    for(int i=1;i<nrv-1;i++) if(ttyp[rv[i]]==4 && m<rmaxm) sidxs[m++]=i;
    sidxs[m]=nrv-1;
    int dd[rmaxm],buy[rmaxm]; bool st[rmaxm];
    for(int j=0;j<m;j++){
        dd[j]=0; st[j]=(j>0);
        for(int i=sidxs[j];i<sidxs[j+1];i++) dd[j]+=efuel(te[re[i]]);
    }
    if(refueldp(m,dd,st,gcap,gcap,gbuy,gstime,buy)<0) return 8;
    return 0;
}

// returns 0 on success else validator/stage code
int attempt(unsigned seed){
    rs=seed; gnodes=0; gobsn=0;
    for(int i=0;i<8;i++) gprune[i]=0;
    tn=gp.n; nte=0; nce=0;
    for(int i=0;i<tn;i++){ ttyp[i]=0; tord[i]=0; tdeg[i]=0; ovu[i]=0; }
    for(int i=0;i<tn;i++){
        for(int tr=0;tr<200;tr++){
            tx[i]=rnd(1000); ty[i]=rnd(1000);
            bool ok=true;
            for(int j=0;j<i;j++){ int dx=tx[i]-tx[j],dy=ty[i]-ty[j]; if(dx*dx+dy*dy<3600) ok=false; }
            if(ok) break;
        }
    }
    for(int i=0;i<tn;i++) for(int j=i+1;j<tn;j++){
        int dx=tx[i]-tx[j],dy=ty[i]-ty[j],l=isqrt(dx*dx+dy*dy);
        if(gp.radius>0 && l>gp.radius) continue;
        gedge& e=ce[nce++]; e.u=i; e.v=j; e.len=l; e.mst=0;
    }
    int idx[ge]; for(int i=0;i<nce;i++) idx[i]=i;
    hsort(idx,nce,clen);
    for(int i=0;i<tn;i++) dsu[i]=i;
    int merges=0;
    for(int k=0;k<nce;k++){
        gedge& c=ce[idx[k]]; int a=fnd(c.u),b=fnd(c.v);
        if(a!=b){ dsu[a]=b; c.mst=1; addedge(c.u,c.v,c.len,0,0,1); merges++; }
    }
    if(merges<tn-1) return 1;
    calchop();
    int cnt=0;
    for(int i=0;i<nce;i++) if(!ce[i].mst){
        hopv[i]=hopm[ce[i].u][ce[i].v];
        if(hopv[i]>=3 && ce[i].len<=gp.maxlen) idx[cnt++]=i;
    }
    hsort(idx,cnt,chop);
    int added=0;
    for(int k=0;k<cnt && added<gp.nextra;k++){
        gedge& c=ce[idx[k]];
        if(tdeg[c.u]>=gp.maxdeg||tdeg[c.v]>=gp.maxdeg) continue;
        int sc=added<gp.nshort, dir=(!sc && added<gp.nshort+gp.noneway);
        addedge(c.u,c.v,c.len,sc,dir,0);
        added++;
    }
    calchop();
    int off=rnd(tn); tstart=-1;
    for(int i=0;i<tn;i++){ int v=(i+off)%tn; if(tdeg[v]>=2){ tstart=v; break; } }
    if(tstart<0) return 2;
    ttyp[tstart]=1;
    ns=0;
    skind[ns]=2; sidx[ns++]=0;
    for(int i=1;i<=gp.k;i++){ skind[ns]=3; sidx[ns++]=i; }
    for(int i=0;i<gp.f;i++){ skind[ns]=4; sidx[ns++]=i; }
    for(int i=0;i<gp.p;i++){ skind[ns]=5; sidx[ns++]=i; }
    soff=rnd(tn);
    if(!place(0)) return 2;
    tfin=sv[0];
    for(int i=0;i<tn;i++) if(ttyp[i]==0 && tdeg[i]==1) ttyp[i]=6;
    for(int i=0;i<nte;i++) isbr[i]=(bfsp(0,-1,i,1)!=tn);
    if(!placeobs(0,0)) return 2;
    return validate();
}

const char* tname[]={"Intersection","Start","Finish","Checkpoint","FuelStation","NitroPickup","DeadEnd"};
void dumpjson(){
    std::cout<<"{\n \"vertices\":[\n";
    for(int i=0;i<tn;i++)
        std::cout<<"  {\"id\":"<<i<<",\"x\":"<<tx[i]<<",\"y\":"<<ty[i]<<",\"type\":\""<<tname[ttyp[i]]
                 <<"\",\"checkpointOrder\":"<<(ttyp[i]==3?tord[i]:-1)<<",\"active\":true}"<<(i+1<tn?",":"")<<"\n";
    std::cout<<" ],\n \"edges\":[\n";
    for(int i=0;i<nte;i++){
        gedge& e=te[i];
        std::cout<<"  {\"id\":"<<i<<",\"from\":"<<e.u<<",\"to\":"<<e.v<<",\"distance\":"<<e.len
                 <<",\"baseTime\":"<<e.len/3<<",\"fuelCost\":"<<e.fuel<<",\"difficulty\":"<<e.diff
                 <<",\"status\":\"Open\",\"isShortcut\":"<<(e.sc?"true":"false")
                 <<",\"directed\":"<<(e.dir?"true":"false")<<",\"obstacle\":"<<(e.obs?"true":"false")<<"}"<<(i+1<nte?",":"")<<"\n";
    }
    std::cout<<" ]\n}\n";
}
#endif
