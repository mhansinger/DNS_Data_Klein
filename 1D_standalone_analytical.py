'''
This is to plot the Histograms from 1D profiles
'''

# %%

import numpy as np
#import matplotlib.pyplot as plt

from scipy.interpolate import interp1d
from scipy.interpolate import splrep, splev

import tikzplotlib


m = 4.4545
beta = 6
alpha = 9/11

raw = np.loadtxt('c_Verlauf_Pfitzner.txt')

xi_org = raw[:,0]
c_org = raw[:,1]

# interpolation function
interp_func = interp1d(xi_org,c_org, kind='cubic')

xi = np.linspace(min(xi_org), max(xi_org), num=5000, endpoint=True)
c_verlauf = interp_func(xi)


# %%

'''
Equations according to: 
Pfitzner, M. A New Analytic pdf for Simulations of Premixed Turbulent Combustion. Flow Turbulence Combust (2020). https://doi.org/10.1007/s10494-020-00137-x
'''

# check function for delta_0:
def compute_delta0(c):
    '''
    Eq. 59
    :param c: LES filtered c value
    :return:
    '''

    return (1 - c ** m) / (1 - c)

def compute_s(c,Delta_LES,m):
    '''
    Eq. 60
    :param c: LES filtered c value
    :param Delta_LES:
    :param m:
    :return:
    '''
    s = np.exp(-Delta_LES/7)*((np.exp(Delta_LES/7) - 1) * np.exp(2 * (c-1) * m) + c)
    return s


# compute the values for c_minus
def compute_c_minus(c,Delta_LES,m):
    '''
    Eq. 61
    :param c: LES filtered c value
    :param Delta_LES:
    :param m:
    :return:
    '''
    this_s = compute_s(c,Delta_LES,m)
    this_delta_0 = compute_delta0(this_s)

    c_min = (np.exp(c * this_delta_0 * Delta_LES) -1) / (np.exp(this_delta_0*Delta_LES) - 1)
    return c_min


def compute_c_m(xi,m):
    '''
    Eq. 12
    :param xi:
    :return:
    '''
    return (1+ np.exp(-m*xi))**(-1/m)

def compute_xi_m(c):
    '''
    Eq. 13
    :param c:
    :return:
    '''
    return 1/m * np.log(c**m /(1-c**m))

def analytical_omega(alpha,beta,c):
    '''
    Eq. 4
    :param alpha:
    :param beta:
    :param c:
    :return:
    '''
    exponent = - (beta * (1 - c)) / (1 - alpha * (1 - c))
    Eigenval = 18.97 #beta**2 / 2 + beta*(3*alpha - 1.344)

    print('Lambda:', Eigenval)

    return Eigenval*((1-alpha*(1-c)))**(-1)*(1-c)*np.exp(exponent)


def compute_c_plus(c_minus,Delta_LES,m):
    '''
    See Section 13 (no equation)
    :param c_minus:
    :param Delta_LES:
    :param m:
    :return:
    '''
    this_xi_m = compute_xi_m(c_minus)

    xi_plus_Delta = this_xi_m+Delta_LES
    this_c_plus = compute_c_m(xi_plus_Delta,m)

    return this_c_plus


def model_omega(c,m):
    '''
    Eq. 15
    :param c:
    :param m:
    :return:
    '''

    return (m+1)*(1-c**m)*c**(m+1)


def compute_flamethickness(m):
    '''
    Eq. 14
    :param m:
    :return:
    '''

    return (m + 1) ** (1 / m + 1) / m


def model_omega_bar(c_plus,c_minus,Delta_LES,m):
    '''
    Eq. 43
    :param c_plus:
    :param c_minus:
    :param Delta_LES:
    :param m:
    :return:
    '''

    return (c_plus**(m+1) - c_minus**(m+1))/Delta_LES


def compute_Delta_DNS(xi,m):
    '''
    Computes the Delta DNS in xi Coordinates
    :param xi:
    :return:
    '''

    flame_thickness = compute_flamethickness(m)

    xi_range = abs(xi[0]) + abs(xi[-1])
    stencil_width = xi_range/len(xi)

    Delta_DNS = stencil_width #* flame_thickness # hier entfernt lauf Pfitzner

    return Delta_DNS



def where_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return np.where(array == array[idx])[0][0]


style = ['b','b--','r','r--']

plt.close('all')

# %%

omega_verlauf = analytical_omega(alpha = alpha, beta = 6, c = c_verlauf)
omega_model = model_omega(c_verlauf,m)

plt.figure()
fig, ax1 = plt.subplots(ncols=1, figsize=(6, 4))

ax2 = ax1.twinx()

UPPER=1#3
LOWER=-1#-5

nr_bins = 70


ax1.plot(xi,c_verlauf,'b-',label=r'$c$')
ax2.plot(xi,omega_verlauf,'r',label=r'$\dot{\omega}$ analytical')
ax2.plot(xi,omega_model,'k',label=r'$\dot{\omega}$ model')
ax2.set_ylabel(r'$\dot{\omega}$ [1/s]', color='k')
ax2.axvspan(LOWER,UPPER, alpha=0.2, color='orange')

ax1.set_ylabel('c [-]', color='b')
ax1.set_xlabel(r"$\xi$", color='k')
plt.title("Progress variable and reaction rate")
ax1.legend(loc='best', bbox_to_anchor=(0, 0, 0.75, 0.75))
ax2.legend(loc='best', bbox_to_anchor=(0, 0, 0.95, 0.95))
plt.xlabel('xi')
plt.xlim([-6,3.5])
tikzplotlib.save('plots/c_all2_%i_%i.tex' % (int(LOWER),int(UPPER)))
#plt.savefig('plots/c_all2_%f_%f.png' % (LOWER,UPPER),format='png')
plt.show(block=False)

# position of filters
low = where_nearest(xi,LOWER)
high = where_nearest(xi,UPPER)


# plot histogram of
plt.figure(figsize=(6, 4))
c_plot=c_verlauf[low:high]
omega_mean = omega_verlauf[low:high].mean()

plt.hist(c_plot,bins=nr_bins,density=True,range=[0,1],)

c_mean=c_plot.mean()
plt.title('$p(c)$')
plt.ylabel('Frequency')
plt.xlabel('$c$')
plt.text(0.12, 3.5, '$\overline{c}=%.3f$' % c_mean,fontsize=20)
plt.text(0.12, 2.8, '$\overline{\dot{\omega}}=%.3f$' % omega_mean,fontsize=20)
tikzplotlib.save('plots/histogram_all_c_%i_%i.tex' % (int(LOWER),int(UPPER)))
#plt.savefig('plots/histogram_all_c_%f_%f.png' % (LOWER,UPPER),format='png')
plt.show()


# %%
# compute Delta_DNS
Delta_DNS = compute_Delta_DNS(xi,m)

Filter_width = [1,5,10,16,24,32,48,96,120,200]

plt.figure()

# loop over the different Filters
for Filter in Filter_width:

    omega_analytic_list = []
    omega_model_list = []
    c_bar_list = []

    Delta_LES = Delta_DNS * Filter

    for i in range(0,len(c_verlauf) - Filter):

        this_c_bar = c_verlauf[i:i + Filter].mean()
        this_analytical_omega_bar = omega_verlauf[i:i + Filter].mean()

        # compute the boundaries:
        this_c_minus = compute_c_minus(c = this_c_bar,Delta_LES=Delta_LES,m=m)
        this_c_plus = compute_c_plus(c_minus=this_c_minus,Delta_LES=Delta_LES,m=m)

        this_model_omega_bar = model_omega_bar(this_c_plus,this_c_minus, Delta_LES=Delta_LES,m=m)

        # print(' ')
        # print('c_bar: %.2f  c_minus: %.2f  c_plus: %.2f  analytical_omega: %.2f  model_omega: %.2f' %
        #       (this_c_bar, this_c_minus, this_c_plus, this_analytical_omega_bar, this_model_omega_bar))

        omega_analytic_list.append(this_analytical_omega_bar)
        omega_model_list.append(this_model_omega_bar)
        c_bar_list.append(this_c_bar)

    # plt.plot(xi[:-Filter],omega_analytic_list)
    # plt.title('omega_numerical')
    # plt.xlabel('xi')
    # plt.savefig('plots/Omega_numerical_xi.png')

    # plt.figure()
    plt.title(r"Delta {LES}=%.3f~Delta {DNS}=%.3f~Filter=%i" % (Delta_LES,Delta_DNS,Filter))
    plt.plot(c_bar_list,omega_analytic_list,'k')
    plt.plot(c_bar_list,omega_model_list,'r')
    plt.xlabel(r"\overline{c}")
    plt.ylabel(r"\overline{\dot{\omega}}")
    plt.legend([r"\overline{\dot{\omega}}_{DNS}",r"\overline{\dot{\omega}}_{model}"])
    #plt.savefig('plots/Vergleich_Delta_LES_%.3f.png' % Delta_LES)

    #plt.figure()
    plt.show(block=False)




















