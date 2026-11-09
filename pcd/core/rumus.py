"""Rumus LaTeX untuk setiap operasi citra.

Nilai pada kamus ini ditampilkan pada panel parameter. Rumus mengikuti
implementasi nyata di ``pcd/core/ops_*.py``, termasuk penjepitan nilai dan
operasi per kanal. Operasi yang hanya mengatur berkas atau membuka tautan
tidak memiliki rumus karena tidak menampilkan parameter.
"""

from __future__ import annotations

RUMUS: dict[str, str] = {
    # ------------------------------------------------------------- Basic Ops
    "basic.negative": r"""
\begin{aligned}
g(x,y) &= 255 - f(x,y) \\
g_c(x,y) &= 255 - f_c(x,y) \quad \text{(mode berwarna)}
\end{aligned}
""",
    "basic.add": r"""
\begin{aligned}
g_c(x,y) &= \mathrm{clip}_{0,255}\!\left(a_c(x,y) + b_c(x,y)\right) \\
f_{\text{abu}} &= \operatorname{gray}(f) \quad \text{(mode grayscale)}
\end{aligned}
""",
    "basic.subtract": r"""
\begin{aligned}
g_c(x,y) &= \mathrm{clip}_{0,255}\!\left(a_c(x,y) - b_c(x,y)\right) \\
f_{\text{abu}} &= \operatorname{gray}(f) \quad \text{(mode grayscale)}
\end{aligned}
""",
    "basic.multiply": r"""
\begin{aligned}
g_c(x,y) &= \mathrm{clip}_{0,255}\!\left(a_c(x,y)\, b_c(x,y)\right) \\
f_{\text{abu}} &= \operatorname{gray}(f) \quad \text{(mode grayscale)}
\end{aligned}
""",
    "basic.divide": r"""
\begin{aligned}
g_c(x,y) &= \mathrm{clip}_{0,255}\!\left(\frac{a_c(x,y)}{b_c(x,y)}\right) \\
f_{\text{abu}} &= \operatorname{gray}(f) \quad \text{(mode grayscale)}
\end{aligned}
""",
    "basic.boolean_not": r"""
\begin{aligned}
g(x,y) &= 255 - f_{\text{abu}}(x,y) \quad \text{(grayscale)} \\
g_c(x,y) &= \sim f_c(x,y) \quad \text{(berwarna, bitwise NOT)}
\end{aligned}
""",
    "basic.boolean_and": r"""
\begin{aligned}
g_c(x,y) &= a_c(x,y) \mathbin{\&} b_c(x,y) \\
f_{\text{abu}} &= \operatorname{gray}(f) \quad \text{(mode grayscale)}
\end{aligned}
""",
    "basic.boolean_or": r"""
\begin{aligned}
g_c(x,y) &= a_c(x,y) \mathbin{|} b_c(x,y) \\
f_{\text{abu}} &= \operatorname{gray}(f) \quad \text{(mode grayscale)}
\end{aligned}
""",
    "basic.boolean_xor": r"""
\begin{aligned}
g_c(x,y) &= a_c(x,y) \oplus b_c(x,y) \\
f_{\text{abu}} &= \operatorname{gray}(f) \quad \text{(mode grayscale)}
\end{aligned}
""",
    "basic.thresholding": r"""
\begin{aligned}
\text{Biner:}\quad g(x,y) &=
\begin{cases}
255, & f_{\text{abu}}(x,y) > T\\
0, & \text{lainnya}
\end{cases}\\
\text{Biner Invers:}\quad g(x,y) &=
\begin{cases}
0, & f_{\text{abu}}(x,y) > T\\
255, & \text{lainnya}
\end{cases}\\
\text{Truncasi:}\quad g(x,y) &= \min\!\left(f_{\text{abu}}(x,y),\,T\right)\\
\text{ToZero:}\quad g(x,y) &=
\begin{cases}
f_{\text{abu}}(x,y), & f_{\text{abu}}(x,y) > T\\
0, & \text{lainnya}
\end{cases}
\end{aligned}
""",
    "basic.convolution": r"""
\begin{aligned}
g_c(x,y) &= \sum_{s=-1}^{1}\sum_{t=-1}^{1} w(s,t)\, f_c(x+s,y+t) \\
w &=
\begin{bmatrix}
w_{00} & w_{01} & w_{02}\\
w_{10} & w_{11} & w_{12}\\
w_{20} & w_{21} & w_{22}
\end{bmatrix}
\end{aligned}
""",
    "basic.fourier": r"""
\begin{aligned}
F(u,v) &= \sum_{x=0}^{M-1}\sum_{y=0}^{N-1} f_{\text{abu}}(x,y)
e^{-j2\pi\left(\frac{ux}{M}+\frac{vy}{N}\right)} \\
S(u,v) &= \left|\operatorname{fftshift}(F)(u,v)\right| \\
g_{\text{spectrum}}(u,v) &= \mathrm{normalize}_{0,255}\!\left(\log(1+S(u,v))\right)
\end{aligned}
""",
    # ------------------------------------------------------------ Colouring
    "color.binary": r"""
\begin{aligned}
g(x,y) &=
\begin{cases}
255, & f_{\text{abu}}(x,y) > 127\\
0, & \text{lainnya}
\end{cases}
\end{aligned}
""",
    "color.grayscale": r"""
\begin{aligned}
g(x,y) &= 0.299\,R(x,y) + 0.587\,G(x,y) + 0.114\,B(x,y)
\end{aligned}
""",
    "color.rgb": r"""
\begin{aligned}
g &= \left[\,R \;\middle|\; G \;\middle|\; B\,\right] \\
&\text{(tiga kanal ditampilkan berdampingan)}
\end{aligned}
""",
    "color.hsv": r"""
\begin{aligned}
V &= \max(R,G,B), \qquad \Delta = V-\min(R,G,B)\\
S &= \begin{cases}
0, & V=0\\
255\Delta/V, & V\neq 0
\end{cases}\\
H^\circ &= \begin{cases}
60(G-B)/\Delta \bmod 360, & V=R\\
60(B-R)/\Delta + 120, & V=G\\
60(R-G)/\Delta + 240, & V=B
\end{cases}\\
H_8 &= \operatorname{round}(H^\circ/2)
\end{aligned}
""",
    "color.cmy": r"""
\begin{aligned}
C &= 255 - R,\qquad M = 255 - G,\qquad Y = 255 - B
\end{aligned}
""",
    "color.yuv": r"""
\begin{aligned}
Y &= 0.299R + 0.587G + 0.114B\\
U &= -0.147R - 0.289G + 0.436B + 128\\
V &= 0.615R - 0.515G - 0.100B + 128
\end{aligned}
""",
    "color.yiq": r"""
\begin{aligned}
Y &= 0.299R + 0.587G + 0.114B\\
I &= \mathrm{clip}_{0,255}\!\left(0.596R - 0.274G - 0.322B + 128\right)\\
Q &= \mathrm{clip}_{0,255}\!\left(0.211R - 0.523G + 0.312B + 128\right)
\end{aligned}
""",
    "color.pseudo": r"""
\begin{aligned}
f_n(x,y) &= \frac{f_{\text{abu}}(x,y)-\min f}{\max f-\min f}\cdot 255\\
g(x,y) &= P_{\mathrm{Turbo}}\!\left(f_n(x,y)\right)
\end{aligned}
""",
    # ------------------------------------------------------ Edge Detection
    "edge.sobel": r"""
\begin{aligned}
G_x &= \begin{bmatrix}-1&0&1\\-2&0&2\\-1&0&1\end{bmatrix} * f_{\text{abu}},
\qquad
G_y = \begin{bmatrix}-1&-2&-1\\0&0&0\\1&2&1\end{bmatrix} * f_{\text{abu}}\\
G &= \sqrt{G_x^2+G_y^2}\\
g &= \mathrm{normalize}_{0,255}\!\left(|G|\right),\qquad
g = 255 \text{ bila } g>T \text{ (ambang aktif)}
\end{aligned}
""",
    "edge.prewitt": r"""
\begin{aligned}
G_x &= \begin{bmatrix}-1&0&1\\-1&0&1\\-1&0&1\end{bmatrix} * f_{\text{abu}},
\qquad
G_y = \begin{bmatrix}-1&-1&-1\\0&0&0\\1&1&1\end{bmatrix} * f_{\text{abu}}\\
g &= \mathrm{normalize}_{0,255}\!\left(\sqrt{G_x^2+G_y^2}\right)
\end{aligned}
""",
    "edge.roberts": r"""
\begin{aligned}
G_x &= \begin{bmatrix}1&0\\0&-1\end{bmatrix} * f_{\text{abu}},
\qquad
G_y = \begin{bmatrix}0&1\\-1&0\end{bmatrix} * f_{\text{abu}}\\
g &= \mathrm{normalize}_{0,255}\!\left(\sqrt{G_x^2+G_y^2}\right)
\end{aligned}
""",
    "edge.laplacian": r"""
\begin{aligned}
\nabla^2 f &= \begin{bmatrix}0&1&0\\1&-4&1\\0&1&0\end{bmatrix} * f_{\text{abu}}\\
g &= \mathrm{normalize}_{0,255}\!\left(\left|\nabla^2 f\right|\right)
\end{aligned}
""",
    "edge.log": r"""
\begin{aligned}
G_\sigma(x,y) &= \frac{1}{2\pi\sigma^2}e^{-\frac{x^2+y^2}{2\sigma^2}}\\
h &= G_\sigma * f_{\text{abu}}\\
g &= \mathrm{normalize}_{0,255}\!\left(\left|\nabla^2 h\right|\right)
\end{aligned}
""",
    "edge.canny": r"""
\begin{aligned}
G &= \sqrt{G_x^2+G_y^2},\qquad \theta = \operatorname{atan2}(G_y,G_x)\\
N(x,y) &= \text{non-maximum suppression}(G,\theta)\\
g(x,y) &=
\begin{cases}
255, & N(x,y) \geq T_{\text{atas}}\\
255, & T_{\text{bawah}} \leq N(x,y) < T_{\text{atas}} \text{ dan terhubung ke tepi kuat}\\
0, & \text{lainnya}
\end{cases}
\end{aligned}
""",
    "edge.compass": r"""
\begin{aligned}
R_k &= \left|K_k * f_{\text{abu}}\right|,\qquad k=1,\ldots,8\\
R_{\max}(x,y) &= \max_k R_k(x,y)\\
g &= \mathrm{normalize}_{0,255}\!\left(R_{\max}\right)
\end{aligned}
""",
    # ---------------------------------------------------------- Enhancement
    "enh.brightness": r"""
\begin{aligned}
g(x,y) &= \mathrm{clip}_{0,255}\!\left(f(x,y)+k\right)
\end{aligned}
""",
    "enh.contrast": r"""
\begin{aligned}
g(x,y) &= \mathrm{clip}_{0,255}\!\left(
\frac{f_{\text{abu}}(x,y)-i_{\min}}{i_{\max}-i_{\min}}
\left(l_{\max}-l_{\min}\right)+l_{\min}
\right)
\end{aligned}
""",
    "enh.hist_equalization": r"""
\begin{aligned}
g(x,y) &= \left\lfloor 255\cdot
\frac{\operatorname{CDF}\!\left(f_{\text{abu}}(x,y)\right)}{MN}
\right\rfloor
\end{aligned}
""",
    "enh.lowpass": r"""
\begin{aligned}
g(x,y) &= \frac{1}{9}
\begin{bmatrix}1&1&1\\1&1&1\\1&1&1\end{bmatrix} * f(x,y)
\end{aligned}
""",
    "enh.median": r"""
\begin{aligned}
g(x,y) &= \operatorname{median}\!\left\{f(s,t)\mid (s,t)\in W_k(x,y)\right\}
\end{aligned}
""",
    "enh.highpass": r"""
\begin{aligned}
g(x,y) &= \mathrm{clip}_{0,255}\!\left(
\begin{bmatrix}-1&-1&-1\\-1&8&-1\\-1&-1&-1\end{bmatrix} * f(x,y)
\right)
\end{aligned}
""",
    "enh.highboost": r"""
\begin{aligned}
f_{\text{low}} &= G_{k\times k} * f\\
g(x,y) &= \mathrm{clip}_{0,255}\!\left(A f(x,y) - (A-1) f_{\text{low}}(x,y)\right)
\end{aligned}
""",
    # ------------------------------------------------------ Frequency Domain
    "freq.ilpf": r"""
\begin{aligned}
D(u,v) &= \sqrt{\left(u-\frac{M}{2}\right)^2+\left(v-\frac{N}{2}\right)^2}\\
H(u,v) &=
\begin{cases}
1, & D(u,v)\leq D_0\\
0, & D(u,v)>D_0
\end{cases}\\
g &= \left|\mathcal{F}^{-1}\!\left(H\cdot\mathcal{F}(f)\right)\right|
\end{aligned}
""",
    "freq.blpf": r"""
\begin{aligned}
D(u,v) &= \sqrt{\left(u-\frac{M}{2}\right)^2+\left(v-\frac{N}{2}\right)^2}\\
H(u,v) &= \frac{1}{1+\left(D(u,v)/D_0\right)^{2n}}\\
g &= \left|\mathcal{F}^{-1}\!\left(H\cdot\mathcal{F}(f)\right)\right|
\end{aligned}
""",
    "freq.ihpf": r"""
\begin{aligned}
D(u,v) &= \sqrt{\left(u-\frac{M}{2}\right)^2+\left(v-\frac{N}{2}\right)^2}\\
H(u,v) &=
\begin{cases}
0, & D(u,v)\leq D_0\\
1, & D(u,v)>D_0
\end{cases}\\
g &= \left|\mathcal{F}^{-1}\!\left(H\cdot\mathcal{F}(f)\right)\right|
\end{aligned}
""",
    "freq.bhpf": r"""
\begin{aligned}
D(u,v) &= \sqrt{\left(u-\frac{M}{2}\right)^2+\left(v-\frac{N}{2}\right)^2}\\
H(u,v) &= 1-\frac{1}{1+\left(D(u,v)/D_0\right)^{2n}}\\
g &= \left|\mathcal{F}^{-1}\!\left(H\cdot\mathcal{F}(f)\right)\right|
\end{aligned}
""",
    # -------------------------------------------------------- Geometrics
    "enh.geom_correction": r"""
\begin{aligned}
x' &= x + s\frac{W}{H}y,\qquad y'=y\\
\begin{bmatrix}x''\\y''\end{bmatrix}
&= R_\theta
\begin{bmatrix}x'-c_x\\y'-c_y\end{bmatrix}
+\begin{bmatrix}c_x\\c_y\end{bmatrix}
\end{aligned}
""",
    "geom.cropping": r"""
\begin{aligned}
g(x,y) &= f(x+x_1,\,y+y_1)\\
0 &\leq x < x_2-x_1,\qquad
0 \leq y < y_2-y_1
\end{aligned}
""",
    "geom.flipping": r"""
\begin{aligned}
\text{Horizontal:}\quad g(x,y) &= f(W-1-x,\,y)\\
\text{Vertikal:}\quad g(x,y) &= f(x,\,H-1-y)\\
\text{Keduanya:}\quad g(x,y) &= f(W-1-x,\,H-1-y)
\end{aligned}
""",
    "geom.rotation": r"""
\begin{aligned}
\begin{bmatrix}x'\\y'\end{bmatrix}
&= R_\theta
\begin{bmatrix}x-c_x\\y-c_y\end{bmatrix}
+\begin{bmatrix}c_x\\c_y\end{bmatrix}\\
R_\theta &=
\begin{bmatrix}\cos\theta&-\sin\theta\\ \sin\theta&\cos\theta\end{bmatrix}\\
c_x &= \left\lfloor W/2 \right\rfloor,\qquad c_y = \left\lfloor H/2 \right\rfloor
\end{aligned}
""",
    "geom.translation": r"""
\begin{aligned}
g(x,y) &= f(x-\Delta x,\; y-\Delta y)
\end{aligned}
""",
    "geom.zooming": r"""
\begin{aligned}
g(x,y) &= f\!\left(\frac{x}{s_x},\,\frac{y}{s_y}\right)\\
W' &= \max\!\left(1,\left\lfloor W s_x\right\rfloor\right),\qquad
H' = \max\!\left(1,\left\lfloor H s_y\right\rfloor\right)
\end{aligned}
""",
    # --------------------------------------------------------------- Noise
    "noise.gaussian": r"""
\begin{aligned}
p(n) &= \frac{1}{\sigma\sqrt{2\pi}}
e^{-\frac{(n-\mu)^2}{2\sigma^2}}\\
g(x,y) &= \mathrm{clip}_{0,255}\!\left(f_{\text{abu}}(x,y)+n(x,y)\right)
\end{aligned}
""",
    "noise.rayleigh": r"""
\begin{aligned}
p(n) &= \frac{n}{\sigma^2}e^{-\frac{n^2}{2\sigma^2}},\qquad n\geq 0\\
g(x,y) &= \mathrm{clip}_{0,255}\!\left(f_{\text{abu}}(x,y)+n(x,y)\right)
\end{aligned}
""",
    "noise.erlang": r"""
\begin{aligned}
p(n) &= \frac{n^{k-1}e^{-n/\lambda}}{\lambda^k\Gamma(k)},\qquad n\geq 0\\
g(x,y) &= \mathrm{clip}_{0,255}\!\left(f_{\text{abu}}(x,y)+n(x,y)\right)
\end{aligned}
""",
    "noise.exponential": r"""
\begin{aligned}
p(n) &= \frac{1}{\mu}e^{-n/\mu},\qquad n\geq 0\\
g(x,y) &= \mathrm{clip}_{0,255}\!\left(f_{\text{abu}}(x,y)+n(x,y)\right)
\end{aligned}
""",
    "noise.uniform": r"""
\begin{aligned}
p(n) &=
\begin{cases}
\dfrac{1}{b-a}, & a\leq n\leq b\\
0, & \text{lainnya}
\end{cases}\\
g(x,y) &= \mathrm{clip}_{0,255}\!\left(f_{\text{abu}}(x,y)+n(x,y)\right)
\end{aligned}
""",
    "noise.impulse": r"""
\begin{aligned}
P(n=255) &= \frac{a}{2},\qquad P(n=0)=\frac{a}{2},\qquad P(n=f)=1-a
\end{aligned}
""",
    # ---------------------------------------------------------- Segmentation
    "seg.otsu": r"""
\begin{aligned}
\omega_0(T) &= \sum_{i=0}^{T}p_i,\qquad
\omega_1(T)=1-\omega_0(T)\\
\mu_0(T) &= \frac{\sum_{i=0}^{T} i p_i}{\omega_0(T)},\qquad
\mu_1(T)=\frac{\sum_{i=T+1}^{255} i p_i}{\omega_1(T)}\\
\sigma_b^2(T) &= \omega_0(T)\omega_1(T)
\left[\mu_0(T)-\mu_1(T)\right]^2\\
T^* &= \arg\max_T \sigma_b^2(T)\\
g(x,y) &=
\begin{cases}
255, & f_{\text{abu}}(x,y)>T^*\\
0, & \text{lainnya}
\end{cases}
\end{aligned}
""",
    "seg.adaptive_mean": r"""
\begin{aligned}
T(x,y) &= \frac{1}{|W|}\sum_{(u,v)\in W}f_{\text{abu}}(x+u,y+v)-C\\
g(x,y) &=
\begin{cases}
255, & f_{\text{abu}}(x,y)>T(x,y)\\
0, & \text{lainnya}
\end{cases}
\end{aligned}
""",
    "seg.adaptive_gaussian": r"""
\begin{aligned}
T(x,y) &= \sum_{(u,v)\in W}G(u,v)f_{\text{abu}}(x+u,y+v)-C\\
g(x,y) &=
\begin{cases}
255, & f_{\text{abu}}(x,y)>T(x,y)\\
0, & \text{lainnya}
\end{cases}
\end{aligned}
""",
    "seg.multi_otsu": r"""
\begin{aligned}
T_1 &= \arg\max_T \sigma_b^2(T)\\
T_2 &= \arg\max_{T>T_1} \sigma_b^2(T\mid T_1)\\
g(x,y) &=
\begin{cases}
0, & f_{\text{abu}}(x,y)\leq T_1\\
127, & T_1<f_{\text{abu}}(x,y)\leq T_2\\
255, & f_{\text{abu}}(x,y)>T_2
\end{cases}
\end{aligned}
""",
    "seg.highlight": r"""
\begin{aligned}
V(x,y) &= \max\!\left(R(x,y),G(x,y),B(x,y)\right)\\
g(x,y) &=
\begin{cases}
f(x,y), & V(x,y)>T\\
(0,0,0), & \text{lainnya}
\end{cases}
\end{aligned}
""",
    "seg.contour": r"""
\begin{aligned}
B(x,y) &=
\begin{cases}
255, & \text{Otsu}\left(f_{\text{abu}}\right)(x,y)=1\\
0, & \text{lainnya}
\end{cases}\\
\{C_i\} &= \mathrm{FindContours}\!\left(B,\ \texttt{RETR\_EXTERNAL},\ \texttt{CHAIN\_APPROX\_SIMPLE}\right)\\
g(x,y) &= \mathrm{DrawContours}\left(f(x,y),\ \{C_i\},\ -1,\ (0,255,0),\ t\right)
\end{aligned}
""",
}

# Rumus alternatif untuk operasi aritmetika dengan satu nilai skalar k.
RUMUS_SKALAR: dict[str, str] = {
    "basic.add": r"""
\begin{aligned}
g_c(x,y) &= \mathrm{clip}_{0,255}\!\left(a_c(x,y) + k\right) \\
f_{\text{abu}} &= \operatorname{gray}(f) \quad \text{(mode grayscale)}
\end{aligned}
""",
    "basic.subtract": r"""
\begin{aligned}
g_c(x,y) &= \mathrm{clip}_{0,255}\!\left(a_c(x,y) - k\right) \\
f_{\text{abu}} &= \operatorname{gray}(f) \quad \text{(mode grayscale)}
\end{aligned}
""",
    "basic.multiply": r"""
\begin{aligned}
g_c(x,y) &= \mathrm{clip}_{0,255}\!\left(a_c(x,y)\, k\right) \\
f_{\text{abu}} &= \operatorname{gray}(f) \quad \text{(mode grayscale)}
\end{aligned}
""",
    "basic.divide": r"""
\begin{aligned}
g_c(x,y) &= \mathrm{clip}_{0,255}\!\left(\frac{a_c(x,y)}{k}\right),
\quad k \neq 0 \\
f_{\text{abu}} &= \operatorname{gray}(f) \quad \text{(mode grayscale)}
\end{aligned}
""",
}


__all__ = ["RUMUS", "RUMUS_SKALAR"]
