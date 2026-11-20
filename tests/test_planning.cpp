#include <iostream>
#include "../src/planning/knapsack.h"
#include "../src/planning/refuel.h"
using namespace std;

// mode 1: m b then m lines "c v"   mode 2: m cap f0 maxbuy stime, d[0..m-1], st[0..m-1]
int main(){
    int mode; cin>>mode;
    if(mode==1){
        int m,b; cin>>m>>b;
        item it[kmaxn]; bool p1[kmaxn],p2[kmaxn];
        for(int i=0;i<m;i++){ it[i].id=i+1; cin>>it[i].c>>it[i].v; }
        int dv=knapdp(it,m,b,p1), gv_=knapgreedy(it,m,b,p2);
        cout<<"dp "<<dv<<" items:"; int cs=0;
        for(int i=0;i<m;i++) if(p1[i]){ cout<<" "<<it[i].id; cs+=it[i].c; }
        cout<<" cost "<<cs<<(cs<=b?" feasible":" INFEASIBLE")<<" states "<<kstates<<"\n";
        cout<<"greedy "<<gv_<<" items:"; cs=0;
        for(int i=0;i<m;i++) if(p2[i]){ cout<<" "<<it[i].id; cs+=it[i].c; }
        cout<<" cost "<<cs<<(cs<=b?" feasible":" INFEASIBLE")<<"\n";
        if(m<=22){ int bv=knapbrute(it,m,b); cout<<"brute "<<bv<<(bv==dv?" match":" MISMATCH")<<"\n"; }
        cout<<(gv_<dv?"greedy strictly worse":"greedy optimal here")<<"\n";
    } else {
        int m,cap,f0,mb,stt; cin>>m>>cap>>f0>>mb>>stt;
        int d[rmaxm],buy[rmaxm]; bool st[rmaxm];
        for(int i=0;i<m;i++) cin>>d[i];
        for(int i=0;i<m;i++){ int x; cin>>x; st[i]=x; }
        int r=refueldp(m,d,st,cap,f0,mb,stt,buy);
        if(r<0){ cout<<"infeasible plan, states "<<rstates<<"\n"; return 0; }
        cout<<"min extra stop time "<<r<<" states "<<rstates<<"\nbuy:";
        for(int i=0;i<m;i++) cout<<" "<<buy[i];
        cout<<"\n";
    }
    return 0;
}
