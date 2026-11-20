#include <iostream>
#include <chrono>
#include "../src/planning/knapsack.h"
using namespace std;

unsigned rs;
int rnd(int m){ rs=rs*1664525u+1013904223u; return (int)((rs>>8)%(unsigned)m); }
double now(){ return chrono::duration<double,micro>(chrono::steady_clock::now().time_since_epoch()).count(); }

// input: seed nsizes then (m b) pairs, then trials for greedy-worse hunt (small m, b)
int main(){
    int seed,ns; cin>>seed>>ns; rs=seed;
    static item it[kmaxn]; static bool p[kmaxn];
    cout<<"m b dpval gval dpstates dp_us greedy_us\n";
    for(int s=0;s<ns;s++){
        int m,b; cin>>m>>b;
        if(m>kmaxn||b>=kmaxb){ cout<<"too big\n"; continue; }
        for(int i=0;i<m;i++){ it[i].id=i+1; it[i].c=1+rnd(b/4+1); it[i].v=1+rnd(100); }
        int dv=0,gv_=0; double t1=0,t2=0;
        knapdp(it,m,b,p);
        for(int r=0;r<5;r++){
            double a=now(); dv=knapdp(it,m,b,p); t1+=now()-a;
            a=now(); gv_=knapgreedy(it,m,b,p); t2+=now()-a;
        }
        cout<<m<<" "<<b<<" "<<dv<<" "<<gv_<<" "<<kstates<<" "<<t1/5<<" "<<t2/5<<"\n";
    }
    int tr,sm,sb; cin>>tr>>sm>>sb;
    int worse=0,bad=0,shown=0;
    for(int t=0;t<tr;t++){
        for(int i=0;i<sm;i++){ it[i].id=i+1; it[i].c=1+rnd(sb/2); it[i].v=1+rnd(30); }
        int dv=knapdp(it,sm,sb,p), g=knapgreedy(it,sm,sb,p), bv=knapbrute(it,sm,sb);
        if(dv!=bv) bad++;
        if(g<dv){
            worse++;
            if(shown<2){
                shown++;
                cout<<"greedy-worse case b="<<sb<<" dp="<<dv<<" greedy="<<g<<" items(c,v):";
                for(int i=0;i<sm;i++) cout<<" ("<<it[i].c<<","<<it[i].v<<")";
                cout<<"\n";
            }
        }
    }
    cout<<"trials "<<tr<<" greedy strictly worse "<<worse<<" dp vs brute mismatches "<<bad<<"\n";
    return 0;
}
