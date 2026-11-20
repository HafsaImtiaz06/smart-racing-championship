#include <iostream>
#include "../src/events/evmgr.h"
using namespace std;

evmgr m;
void cb(int t){ cout<<"reroute at "<<t<<"\n"; }

// header: ne nv evcap. commands: S e | T v base | P v | A type t target val dur | C id | R t | K v | Q e v | L | X
int main(){
    int ne,nv,ec; cin>>ne>>nv>>ec;
    m.init(ne,nv,ec); m.cb=cb;
    char c;
    while(cin>>c){
        if(c=='S'){ int e; cin>>e; m.isshort[e]=true; }
        else if(c=='T'){ int v,b; cin>>v>>b; m.setstation(v,b); }
        else if(c=='P'){ int v; cin>>v; m.ispick[v]=true; }
        else if(c=='A'){ int ty,t,tg,val,dur; cin>>ty>>t>>tg>>val>>dur; cout<<"add -> "<<m.add(ty,t,tg,val,dur)<<"\n"; }
        else if(c=='C'){ int id; cin>>id; cout<<"cancel -> "<<m.cancel(id)<<"\n"; }
        else if(c=='K'){ int v; cin>>v; cout<<"collect -> "<<m.collect(v)<<"\n"; }
        else if(c=='R'){ int t; cin>>t; m.run(t); }
        else if(c=='Q'){ int e,v; cin>>e>>v;
            cout<<"edge "<<e<<" status "<<m.status(e)<<" oil "<<m.oilpen(e)<<" cap "<<m.speedcap(e)
                <<" | vertex "<<v<<" station "<<m.stationon(v)<<" pickup "<<m.pickupon(v)<<"\n"; }
        else if(c=='L') m.printlog();
        else if(c=='X') break;
    }
    cout<<"applied "<<m.napplied<<" lazy "<<m.nlazy<<" rejected "<<m.nrej<<" invalid "<<m.ninvalid<<"\n";
    return 0;
}
