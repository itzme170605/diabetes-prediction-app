from __future__ import division
from pylab import *
from numpy import *
from scipy.integrate import *
from time import *

init_time = time();

def myplot(sbplt,ts,Xs,xl='',xt=0,yl='',yt=1,lbl=''):
    subplot(sbplt[0],sbplt[1],sbplt[2]);
    plot(ts,Xs,linewidth=2,label=lbl);
    xlabel(xl,fontsize=13); 
    if xt==0:
        xticks([],fontsize=13);
    else:
        xticks([0,int(ts[-1]/2),int(ts[-1])],fontsize=13);
    if yt==0:
        yticks([],fontsize=13);
    else:
        yticks(fontsize=13);
    ylabel(yl,fontsize=13); 
    return '';

eps=0.1;

def percent(x,y):
    return (x-y)/x*100;
def Hill(x,x0,n=2):
    return x**n/(x**n+(1*x0)**n);
def plus(x):
    return x*(x>=0)
def myequal(x,x0,eps):
    return abs(x-x0)<=eps;
def F(x,x0,n):
    return (1-1*Hill(x%(6/24),x0/24,n));

def T2DM_params(x,t,m=0): 
    # m: 0 if noob+nodiab, 1 if ob, 2 if diab, 3 if ob+diab
    B,A,L,I, U2,U4,C,G, Gs, Ta, O,P=x;
    Gss=1e-3*Hill(t,3/24,-6);
    #Ta=Ta*(m in [1,3]);
    Linh=1/(1+L/(1*tKL));
    Lfrac=Hill(L,1*KL,1); Iofrac=Hill(plus(Io-I),1*KI,1); Lfrac=Hill(plus(L-Lo),1*KL,1);
    U2frac=U2/(KU2+U2); U4frac=U4/(1*KU4+U4); 
    Oinh=1/(1+O/KO); Tainh=1/(1+etaTa*Ta);
    
    cst_dose=1;
    def lamL(x,x0=1,n=6):
        if myequal((x)%(1),18/24,eps)==1 and x>eps:
            return 0*tlamL*(1-Hill(x%(6/24),x0/24,n));
        else:
            if myequal((x)%(1),12/24,eps)==1:
                return dinner_dose*tlamL*((x<=24/24)+cst_dose*(x>24/24))*(1-Hill(x%(6/24),x0/24,n));
            elif myequal((x)%(1),6/24,eps)==1:
                return lunch_dose*tlamL*((x<=24/24)+cst_dose*(x>24/24))*(1-Hill(x%(6/24),x0/24,n));
            else:
                return breakfast_dose*tlamL*((x<=24/24)+cst_dose*(x>24/24))*(1-Hill(x%(6/24),x0/24,n));
    def muIG(x):
        return 1*tmuIG*(1*Hill(x%(6/24),1/24,4));
    def lamG(x,x0,n=4):
        if myequal((x)%(1),18/24,eps)==1 and x>eps:
            return 0*tlamG*(1-1*Hill(x%(6/24),x0/24,n));
        else:
            if myequal((x)%(1),12/24,eps)==1:
                return dinner_dose*tlamG*((x<=24/24)+cst_dose*(x>24/24))*(1-1*Hill(x%(6/24),x0/24,n));
            elif myequal((x)%(1),6/24,eps)==1:
                return lunch_dose*tlamG*((x<=24/24)+cst_dose*(x>24/24))*(1-1*Hill(x%(6/24),x0/24,n));
            else:
                return breakfast_dose*tlamG*((x<=24/24)+cst_dose*(x>24/24))*(1-1*Hill(x%(6/24),x0/24,n));
    def lamsG(x,x0=1,n=4):
        if myequal((x)%(1),18/24,eps)==1 and x>eps:
            return 0*tlamsG*(1-1*Hill(x%(6/24),x0/24,n))*G;
        else:
            if myequal((x)%(1),12/24,eps)==1:
                return dinner_dose*tlamsG*((x<=24/24)+cst_dose*(x>24/24))*(1-1*Hill(x%(6/24),x0/24,n))*G;
            elif myequal((x)%(1),6/24,eps)==1:
                return lunch_dose*tlamsG*((x<=24/24)+cst_dose*(x>24/24))*(1-1*Hill(x%(6/24),x0/24,n))*G;
            else:    
                return breakfast_dose*tlamsG*((x<=24/24)+cst_dose*(x>24/24))*(1-1*Hill(x%(6/24),x0/24,n))*G;
    def lamP(x,x0=1,n=6):
        if myequal((x)%(1),18/24,eps)==1 and myequal((x)%(1),6/24,eps)==0 and myequal((x)%(1),12/24,eps)==0 and myequal((x)%(1),0/24,eps)==0 and x>eps:
            return 0;
        else:
            if myequal((x)%(1),12/24,eps)==1 and myequal((x)%(1),6/24,eps)==0 and myequal((x)%(1),18/24,eps)==0 and myequal((x)%(1),0/24,eps)==0:
                return dinner_dose*gamP*F(x,x0,n);
            elif myequal((x)%(1),6/24,eps)==1 and myequal((x)%(1),12/24,eps)==0 and myequal((x)%(1),18/24,eps)==0 and myequal((x)%(1),0/24,eps)==0:
                return lunch_dose*gamP*F(x,x0,n);
            elif myequal((x)%(1),0/24,eps)==1 and myequal((x)%(1),6/24,eps)==0 and myequal((x)%(1),12/24,eps)==0 and myequal((x)%(1),18/24,eps)==0:
                return breakfast_dose*gamP*F(x,x0,n);
            else: return 0;
    def lamO(x,x0=1,n=6):
        if myequal((x)%(1),18/24,eps)==1 and myequal((x)%(1),6/24,eps)==0 and myequal((x)%(1),12/24,eps)==0 and myequal((x)%(1),0/24,eps)==0 and x>eps:
            return 0;
        else:
            if myequal((x)%(1),12/24,eps)==1 and myequal((x)%(1),6/24,eps)==0 and myequal((x)%(1),18/24,eps)==0 and myequal((x)%(1),0/24,eps)==0:
                return dinner_dose*gamO*F(x,x0,n);
            elif myequal((x)%(1),6/24,eps)==1 and myequal((x)%(1),12/24,eps)==0 and myequal((x)%(1),18/24,eps)==0 and myequal((x)%(1),0/24,eps)==0:
                return lunch_dose*gamO*F(x,x0,n);
            elif myequal((x)%(1),0/24,eps)==1 and myequal((x)%(1),6/24,eps)==0 and myequal((x)%(1),12/24,eps)==0 and myequal((x)%(1),18/24,eps)==0:
                return breakfast_dose*gamO*F(x,x0,n);
            else: return 0;
    
    dL = lamL(t) - 1*(1*muLB*B*L + 1*muLA*A*L);
    dA = 1*lamA*Iofrac*Linh/1 - muA*A;
    dB = tlamB*Lfrac/1 - muB*B*(1+xi1*G+xi2*P);
    dI = 1.*lamIB*B - 1*muI*I - tmuIG*G*I;
    
    dC = 1*lamCA*A*(1+gam2*((xi3-G)>0)*L)/(1+gam1*((G-xi4)>0)*L) - muC*C;
    dU2 = 1.*lamU2C*C - 1*muU2*U2;
    dU4 = 1*lamU4I*I*Tainh/1 - muU4*U4;
    #x0=0.3*(m==0)+0.53*(m==1)+0.66*(m in [2,3]); n=4;
    x0=0.3 + (0*(t%1<=6/24) + 0.1*(6/24<t%1<=12/24) + 0.3*(12/24<t%1)); n=4;

    dG = lamG(t,x0,n)/1 - 1*lamsG(t)/1 - 1*(1.05*(m==0)+5.5/4*(m==1)+5/4*(m in[2,3]))*lamGU4*G*U4frac/1 + 1.*lamGsU2*Gs*U2frac/2;
    
    cst=(1*(t%1<=6/24) + 1.*(6/24<t%1<=12/24) + 3*(12/24<t%1));
    dGs = 1*lamsG(t) - cst*lamGsU2*Gs*U2frac/1. + 1*lamGU4*G*U4frac/1;
    
    dTa = 1*lamTa + 1.15*lamTaP*P*Oinh - 1*muTa*Ta; # m=1,3 is ob and ob+diab
    
    dO = 1*lamO(t,x0,n)/1 - muO*O;
    dP = 1*lamP(t,x0,n)/1 - 1*muP*P/1;
    
    dO = (0+1*cstP)*lamO(t,x0,n)/(0+1*cstP) - 1*muO*O/(1);
    dP = (0+1*(cstP+hcstP))*lamP(t,x0,n)/1 - 1*muP*P/((1*(cstP==1)+(50*(cstP!=1)))*cstP);
    #dO = (lamOh*(m==0)+lamOo*(m!=0))*dG;
    #dP = (cstP*lamPh*(m==0)+lamPo*(m!=0))*dG;
    return [dB,dA,dL,dI, dU2,dU4,dC,dG, dGs, dTa, dO,dP];

cstP=1; hcstP=0;
BFld=[1,0.5,0.5]; bfLd=[0.5,1,0.5]; bflD=[0.4,0.4,0.8];
breakfast_dose,lunch_dose,dinner_dose=bflD;
tl1=10; tl2=10; tk1=100; tk2=25; xi1=1e12; xi2=1e12; xi3=1e-2; xi4=1e-4;
KC=6e-16;
# Increase Io to or decrease Ir increase G
Co=4.8e-16; Cr=4.87e-16; Io=0.8e-13; Ir=3.8e-13; Lo=0.3e-14; Ir=3.82e-13;

muU2=4.62; muU4=1.85; muC=166.22; Gs=1e-3; muO=0.57*24; muP=0.5*24; gamO=1.83e-3/5; gamP=3.66e-3/800;
KU2=9.45e-6; KU4=2.78e-6; KG=2e-3;
lamU2C=6.6e10; lamU4I=4.17e7; lamCA=1.65e-11; lamGU4=4*0.387; lamGsU2=4.644;
gam1=1e14; gam2=1.2e14; tlamG=0.21/5; tlamsG=19*0.5845;

muB=1*8.32/1; muA=1*8.32/1; muI=198.04; muLB=2.51e2; muLA=2.51e2; muTa=199;
lamA=0.35; tlamB=1.745e9;
lamB=0.0154e16; tlamL=4.95e-13; tmuIG=6e5; lamIB=12*1.05e-9; lamTa=7.96e-10; lamTaP=3.26e-4; lamTa=1.19e-9;
KL=1.5e-14; tKL=1.5*1e-14; KI=2e-13; KO=1.36e-6; O=KO; P=2.44e-6; 
Ph=1.22e-6; Oh=6.78e-7; Oo=1.36e-6; Po=2.44e-6; #lamO=2700; lamP=3000;
#lamOh=lamO*Oh; lamPh=lamP*Ph; lamOo=lamO*Oo; lamPo=lamP*Po;
A0=1e-3; B0=3.4e-3; 

nberweek=2;
totaltime=1*24/24; Ndt=3*2400; dt=totaltime/Ndt;
runtspan=linspace(1e-10,totaltime,Ndt); tspan=runtspan;
dailyidx_set=[0];
for t in range(int(totaltime)+1):
    dum_set=[];
    for i in range(Ndt): 
        if t<=tspan[i]<t+1:
            dum_set+=[i];
    dailyidx_set+=[max(dum_set)];
         
Days=[round(tspan[i]) for i in dailyidx_set[0:]];
print(Days)

m_set=[0]; # 0: normal health, 1: prediabetes, 2: obesity+diabetes

B_0=13e-3; A_0=5e-3; L_0=4.5e-15; I_0=0.97e-13; 
U2_0=1*9e-6; U4_0=0.993*2.6e-6; C_0=4.964e-16; G_0=1.1e-3; 
Gs_0=0.9e-3; Ta_0=5.65e-12; P_0=Ph; O_0=Oh;
X0=[B_0,A_0,L_0,I_0, U2_0,U4_0,C_0,G_0, Gs_0, Ta_0, O_0,P_0];

for m in m_set:
    eta0=1e10; cst=[1, 10, 100, 1000];
    etaTa = eta0*( cst[0]*(m in [0]) + cst[1]*(m in [1]) + cst[2]*(m in [2]) + cst[3]*(m in [3]) );
    G_0 = 1e-3*( 0.95*(m in [0]) + 1.15*(m in [1]) + 1.8*(m in [2,3]) )
    X0=[B_0,A_0,L_0,I_0, U2_0,U4_0,C_0,G_0, Gs_0, Ta_0, O_0,P_0];
    X=odeint(T2DM_params,X0,tspan,(m,),mxstep=50000);
    B=X[:,0]/2.5; A=X[:,1]; L=X[:,2]; I=X[:,3]; U2=X[:,4]; U4=X[:,5]; C=X[:,6]; G=X[:,7]; Gs=X[:,8]; Ta=X[:,9]; O=X[:,10]; P=X[:,11]; E=Gs+G;
    Edays=array([E[i] for i in dailyidx_set[0:]]);
    lb=('Normal'+' ('+str(cst[0])+'$\\eta_{T_\\alpha}$)')*(m==0)+('Prediabetes'+' ('+str(cst[1])+'$\\eta_{T_\\alpha}$)')*(m==1)+('Diabetes'+' ('+str(cst[2])+'$\\eta_{T_\\alpha}$)')*(m==2)+('Diab+Obes'+' ('+str(cst[3])+'$\\eta_{T_\\alpha}$)')*(m==3);
    #lb='';
    
    if m==0:
        figure(2014);
        myplot((4,3,1),tspan[0:]*24,B[0:]*1e3,xl='',xt=0,yl='B ($10^{-3}$)',yt=1,lbl=lb);
        myplot((4,3,2),tspan[0:]*24,A[0:]*1e3,xl='',xt=0,yl='A ($10^{-3}$)',yt=1,lbl=lb);
        myplot((4,3,3),tspan[0:]*24,L[0:]*1e14,xl='',xt=0,yl='L ($10^{-14}$)',yt=1,lbl=lb);
        myplot((4,3,4),tspan[0:]*24,I[0:]*1e13,xl='',xt=0,yl='I ($10^{-13}$)',yt=1,lbl=lb);
        myplot((4,3,5),tspan[0:]*24,U2[0:]*1e6,xl='',xt=0,yl='$U_2$ ($10^{-6}$)',yt=1,lbl=lb);
        myplot((4,3,6),tspan[0:]*24,U4[0:]*1e6,xl='',xt=0,yl='$U_4$ ($10^{-6}$)',yt=1,lbl=lb);
        myplot((4,3,7),tspan[0:]*24,C[0:]*1e16,xl='',xt=0,yl='C ($10^{-16}$)',yt=1,lbl=lb);
        myplot((4,3,8),tspan[0:]*24,G[0:]*1e3,xl='',xt=0,yl='G ($10^{-3}$)',yt=1,lbl=lb);
        myplot((4,3,9),tspan[0:]*24,Gs[0:]*1e3,xl='Hours',xt=1,yl='$G^*$ ($10^{-3}$)',yt=1,lbl=lb);
        #myplot((4,3,10),tspan[0:]*24,Gss[0:]*1e3,xl='Hours',xt=1,yl='$G^{**}$ ($10^{-3}$)',yt=1,lbl=lb);
        myplot((4,3,10),tspan[0:]*24,E[0:]*1e3,xl='Hours',xt=1,yl='E $(10^{-3})$',yt=1,lbl=lb);
        myplot((4,3,11),tspan[0:]*24,Ta[0:]*1e12,xl='Hours',xt=1,yl='$T_\\alpha$ ($10^{-12}$)',yt=1,lbl=lb);
        
        #figure(2)
        #myplot((1,3,1),tspan[0:]*24,G[0:]*1e3,xl='Hours',xt=1,yl='G ($10^{-3}$)',yt=1,lbl=lb); plot(tspan[0:]*24,[1.00 for x in tspan[0:]],'k--'); plot(tspan[0:]*24,[1.40 for x in tspan[0:]],'r--');
        #myplot((1,3,2),tspan[0:]*24,O[0:]*1e6,xl='Hours',xt=1,yl='O ($10^{-6}$)',yt=1,lbl=lb); plot(tspan[0:]*24,[0.678 for x in tspan[0:]],'k--');
        #myplot((1,3,3),tspan[0:]*24,P[0:]*1e6,xl='Hours',xt=1,yl='P ($10^{-6}$)',yt=1,lbl=lb); plot(tspan[0:]*24,[1.22 for x in tspan[0:]],'k--');
     
    
    if m==0:
        figure(201701)
        myplot((1,1,1),tspan[0:]*24,G[0:]*1e3,xl='Hours',xt=1,yl='G ($10^{-3}$)',yt=1,lbl=lb); #legend(loc='best',fontsize=15);
        plot(tspan[0:]*24,[1.00 for x in tspan[0:]],'k--'); plot(tspan[0:]*24,[1.40 for x in tspan[0:]],'r--');
        title('Glucose',fontsize=15); #plt.arrow(11, 1, 0, -0.1, head_width = 0.42, width = 0.105, ec ='black')
        
        figure(201702)
        myplot((1,1,1),tspan[0:]*24,E[0:]*1e3,xl='Hours',xt=1,yl='E ($10^{-3}$)',yt=1,lbl=lb); #legend(loc='best',fontsize=15);
        #plot(tspan[0:]*24,[E[0]*1e3 for x in tspan[0:]],'k--'); #plot(tspan[0:]*24,[E[0] for x in tspan[0:]],'r--');
        title('(B) Total Energy',fontsize=15); #plt.arrow(11, 1, 0, -0.1, head_width = 0.42, width = 0.105, ec ='black')
        
        figure(201703)
        plot(Days*1,Edays*1e3,'-*',markersize=3);
        xlabel('Days',fontsize=13); ylabel('E ($10^{-3}$)',fontsize=13);
        #myplot((1,1,1),dailyidx_set*24,Edays[0:]*1e3,xl='Hours',xt=1,yl='E ($10^{-3}$)',yt=1,lbl=lb); #legend(loc='best',fontsize=15);
        plot(tspan[0:]*1,[E[0]*1e3 for x in tspan[0:]],'k--'); #plot(tspan[0:]*24,[E[0] for x in tspan[0:]],'r--');
        title('(A) Normal health',fontsize=15); #plt.arrow(11, 1, 0, -0.1, head_width = 0.42, width = 0.105, ec ='black')
    elif m==1:
        figure(20171)
        myplot((1,3,2),tspan[0:]*24,G[0:]*1e3,xl='Hours',xt=1,yl='',yt=1,lbl=lb); #legend(loc='best',fontsize=15);
        plot(tspan[0:]*24,[1.00 for x in tspan[0:]],'w--'); plot(tspan[0:]*24,[1.25 for x in tspan[0:]],'k--'); plot(tspan[0:]*24,[1.40 for x in tspan[0:]],'r--'); plot(tspan[0:]*24,[1.99 for x in tspan[0:]],'r--');
        title('(B) Prediabetes',fontsize=15);
    else:
        figure(20172)
        myplot((1,1,1),tspan[0:]*24,G[0:]*1e3,xl='Hours',xt=1,yl='Glucose (G, $10^{-3}$)',yt=1,lbl=lb); #legend(loc='best',fontsize=15);
        plot(tspan[0:]*24,[1.26 for x in tspan[0:]],'w--'); plot(tspan[0:]*24,[2.00 for x in tspan[0:]],'r--');
        title('Type 2 Diabetes with Obesity',fontsize=15);
        
        
    

end_time = (time() - init_time)/60;
print('%f minutes'%end_time)

show();