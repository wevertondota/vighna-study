"""Âncora isolada da logo oficial do VighnaStudy no Dashboard.

Sem faixa, moldura ou campo de busca. Preserva a posição da logo e o espaço
no layout original. Não modifica o cabeçalho exclusivo do portal Início.
"""

from PySide6.QtCore import Qt, QSize, QRectF, QObject, QEvent, QTimer, QPoint, QPointF
from PySide6.QtGui import (QPixmap, QPainter, QColor, QLinearGradient, QPen,
                           QBrush, QPainterPath, QIcon, QRadialGradient, QFont)
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QPushButton, QWidget,
                              QProgressBar, QSizePolicy, QVBoxLayout, QSpacerItem)

from ui.design import render_native_qss, render_qss
from ui.vighnastudy_brand_home import assinatura_cabecalho_png


QSS_CABECALHO_DASHBOARD = r"""
QFrame#dashboardQuickNav {
    /* A faixa do Dashboard desaparece; somente a logo permanece na posição.
       O cabeçalho independente da Home não utiliza este seletor. */
    background: transparent;
    border: none;
    border-radius: 0px;
}
/* Progresso horizontal, calibrado pela referência visual (imagem 2).
   Escopo LOCAL: não afeta barra da meta diária ou progresso em outras telas. */
QFrame#dashboardTopProgressPanel {
    background-color: rgba(3, 20, 45, 218);
    border: 1px solid #1169B1;
    border-radius: 13px;
}
QFrame#dashboardTopProgressPanel QLabel {
    background: transparent;
    border: none;
    color: #F5FBFF;
}
QLabel#dashboardTopProgressLevel {
    font-size: 12pt;
    font-weight: 750;
    color: #FFFFFF;
}
QLabel#dashboardTopProgressXP {
    font-size: 9pt;
    color: #E7F5FF;
}
QProgressBar#dashboardTopProgressBar {
    background-color: #08386B;
    border: none;
    border-radius: 5px;
}
QProgressBar#dashboardTopProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                                stop:0 #1065FF,stop:0.55 #00B9F7,stop:1 #00E6F5);
    border-radius: 5px;
}
QPushButton#dashboardTopAchievements {
    color: #F7FCFF;
    background: transparent;
    border: none;
    border-left: 2px solid #1269B8;
    border-radius: 0px;
    font-size: 9pt;
    font-weight: 650;
    padding-left: 7px;
    padding-right: 2px;
    text-align: left;
}
QPushButton#dashboardTopAchievements:hover,
QPushButton#dashboardTopAchievements:focus {
    color: #FFFFFF;
    background-color: rgba(4, 100, 170, 45);
}
/* Planejamento modular da referencia. Somente o topo do Dashboard Futurista. */
QFrame#dashboardTopPlanningStrip {
    background-color: rgba(3, 19, 42, 211);
    border: 1px solid #007DAB;
    border-radius: 13px;
}
QFrame#dashboardTopPlanningStrip QLabel {
    background: transparent;
    border: none;
}
QFrame#dashboardTopPlanningStrip QLabel#dashboardTopPlanningIcon {
    background-color: rgba(0, 41, 66, 230);
    border: 1px solid #00D5E5;
    border-radius: 10px;
}
QFrame#dashboardTopPlanningStrip QLabel#dashboardTopPlanningTitle {
    color: #F4FBFF;
    font-size: 10pt;
    font-weight: 750;
}
QFrame#dashboardTopPlanningStrip QLabel#dashboardTopPlanningDate {
    color: #D7E5F3;
    font-size: 9pt;
}
QFrame#dashboardTopPlanningStrip QLabel#dashboardTopPlanningQuestions {
    color: #F8FCFF;
    font-size: 10pt;
    font-weight: 750;
}
QFrame#dashboardTopPlanningStrip QLabel#dashboardTopPlanningPercent {
    color: #F2F8FF;
    font-size: 9pt;
}
QFrame#dashboardTopPlanningStrip QLabel#dashboardTopPlanningRevisions {
    color: #F5FBFF;
    font-size: 9pt;
    font-weight: 700;
}
QFrame#dashboardTopPlanningSeparator {
    background-color: #0C6D88;
    border: none;
}
QProgressBar#dashboardTopPlanningBar {
    background-color: #0B3155;
    border: none;
    border-radius: 4px;
}
QProgressBar#dashboardTopPlanningBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                                stop:0 #0879F8,stop:0.5 #00BDF1,stop:1 #00E0E9);
    border-radius: 4px;
}
QLabel#dashboardQuickBrand {
    background-color: transparent;
    border: none;
}
QLabel#dashboardQuickBrandName {
    background-color: transparent;
    color: {{color:text.primary}};
    border: none;
    font-size: 13pt;
    font-weight: 700;
}
"""


def _icone_trofeu_referencia():
    """Icone de trofeu dourado, com acabamento e proporcao da referencia.

    O desenho permanece exclusivo do painel de conquistas do Dashboard.
    Renderizacao em alta resolucao e normalizacao pelo QIcon na interface.
    """
    img = QPixmap(96, 96)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setRenderHint(QPainter.SmoothPixmapTransform, True)
    p.scale(1.5, 1.5)  # Coordenadas logicas de 64 px.

    ouro = QLinearGradient(8, 11, 53, 53)
    ouro.setColorAt(0.00, QColor("#FFF7B8"))
    ouro.setColorAt(0.32, QColor("#FFCF42"))
    ouro.setColorAt(0.72, QColor("#F5A600"))
    ouro.setColorAt(1.00, QColor("#C96B00"))
    p.setPen(QPen(QColor("#B87403"), 1.35))
    p.setBrush(QBrush(ouro))
    # Alcas maiores do que na R1: preenchem o icone como na referencia.
    esquerda = QPainterPath()
    esquerda.moveTo(15, 13)
    esquerda.cubicTo(3, 8, 5, 33, 20, 34)
    esquerda.lineTo(22, 28)
    esquerda.cubicTo(13, 29, 10, 19, 15, 19)
    esquerda.closeSubpath()
    p.drawPath(esquerda)
    direita = QPainterPath()
    direita.moveTo(48, 13)
    direita.cubicTo(61, 8, 59, 33, 43, 34)
    direita.lineTo(41, 28)
    direita.cubicTo(51, 29, 55, 19, 48, 19)
    direita.closeSubpath()
    p.drawPath(direita)
    corpo = QPainterPath()
    corpo.moveTo(14, 10)
    corpo.lineTo(49, 10)
    corpo.cubicTo(49, 33, 44, 42, 32, 44)
    corpo.cubicTo(19, 42, 14, 33, 14, 10)
    corpo.closeSubpath()
    p.drawPath(corpo)
    # Brilho limitado na borda do calice; evita visual plano/emoji.
    p.setPen(QPen(QColor("#FFF6AD"), 2.2))
    p.drawLine(17, 12, 45, 12)
    p.setPen(QPen(QColor("#FFE38A"), 1.8))
    p.drawLine(19, 17, 19, 28)
    p.setPen(QPen(QColor("#AC6400"), 1.0))
    p.setBrush(QBrush(ouro))
    p.drawRoundedRect(QRectF(28, 43, 8, 10), 1.4, 1.4)
    p.drawRoundedRect(QRectF(22, 52, 20, 4), 1.1, 1.1)
    p.drawRoundedRect(QRectF(16, 56, 32, 5), 1.3, 1.3)
    p.end()
    return QIcon(img)

def _icone_calendario_planejamento():
    """Calendario ciano vetorial: evita glyphs dependentes do Windows."""
    image = QPixmap(88, 88)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.scale(2, 2)
    # corpo de calendario e argolas superiores
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor("#00D6E8"))
    painter.drawRoundedRect(QRectF(6, 9, 32, 30), 4.0, 4.0)
    painter.setPen(QPen(QColor("#004565"), 2.2))
    painter.drawLine(9, 17, 35, 17)
    painter.setPen(QPen(QColor("#00EEFA"), 3.3))
    painter.drawLine(14, 5, 14, 13)
    painter.drawLine(30, 5, 30, 13)
    check = QPainterPath()
    check.moveTo(12, 27)
    check.lineTo(19, 33)
    check.lineTo(32, 22)
    painter.setPen(QPen(QColor("#023D53"), 3.3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.setBrush(Qt.NoBrush)
    painter.drawPath(check)
    painter.end()
    return image


def _icone_revisoes_planejamento():
    """Bloco ciano com ondas escurecidas, como na referencia."""
    image = QPixmap(64, 64)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.scale(2, 2)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor("#00D8E8"))
    painter.drawRoundedRect(QRectF(1.5, 1.5, 29, 29), 3.0, 3.0)
    painter.setPen(QPen(QColor("#025075"), 2.25, Qt.SolidLine, Qt.RoundCap))
    for y in (12, 20):
        wave = QPainterPath()
        wave.moveTo(6.5, y)
        wave.cubicTo(10, y - 5, 13, y + 4, 16, y)
        wave.cubicTo(19, y - 5, 22, y + 4, 26, y)
        painter.drawPath(wave)
    painter.end()
    return image





# Cristal Energetico V5 - Ouro e Ciano, confirmado na referencia visual.
# PNG RGBA nativo 80 x 80, emblema puro, sem o numero do nivel.
# Fonte dos dados e geometria do HUD continuam inalteradas.
def _crystal_option4_png():
    import base64 as _b64
    import zlib as _zlib
    payload = (
        'c-jHWI5fwJP)<h;3K|Lk000e1NJLTq002+`002-31^@s6juG;$0020WNkl<Zc-'
        'p<3cbHvAdH=uflylDQ+js9al~wPyY{@E?Ez2192F7$u3897(5?T@<3FJo&kkCU924fqH3+~3UY^(R)>o(o3x1KWP_s6c})mk=?nB3=?=bm%+w)yP$Z8LKQ_{'
        '%=%JdKTMd`y!7ya}01Rdu!3cEb&qFFSeo@n=t;e0tv}{_b7Zd!9F;wY9YdKy382V$6HlxHkSf|6&jE7X){{b9$L;3;^krW#ydZbt#rk%3y9R?xeFB)!_S<IZ'
        'h<T{1fbG!?@$I4||^PwXbAH*<VO;cnRgv80DSw+zPPzdhi5EF9?7e7pax^?zK*rX~g1=;<bR4M4?*)i0q5sKlYf;^Gq-'
        'E&;4IL`2P{OGacb$uVu4fi3E5&4j#q8JumGHmE!IPZxEAOF1_uuk5;atWi#7lQ;nU`6s}wQyJr%o8Yf1!M4?G0!BQzuIt{9-'
        '0_F2B0`_uhf5l9jy@KG*_XEfKJC@CY*VjYT)<Oh9jR?bP5r!ENMQNE%Cz6AMUG%2gm%r`F=*mX!#zIdREhgR~Uh}$Z-|zcJVw~3|!Z788VMc^uwFrV5QK>-'
        'G*F!Wmg15H5$REC(PyAnl<gbvQd#NCCMrk~e0P{R>rE0iR4o{^#&X^WLXfA~1H8s*Zc8tkyexPw-IQ#W~|J$L<D-'
        '+WZzqBJ3EAtrYtCH;(Wwsvr_OFKyPMHFslrmBpCZ%DX7o&37W7Z}}sR~P{N0eDCzO3S25wm80NqA?}7KY$qSS=EXjPSfj#$s9up`?_al+u$t>A0TfC5<V@FS'
        '%mrJ07cCo{&sy%Ox=`K}J(pbvavp)phTlHK|ZXlujfP(mVTpuAEp*OV5jBB9RfkpOHaOBkJqHv)MlyssC3H`ClSPoKaj9fk#nBjHpcs<r?8qOfbfU<D@t|l8'
        '{U^Wn^sYRv~`%xyH**w!QVePZTa5PO!49i957nO56omUIEkf^-'
        'YblyiNUI{mJmoY12HZwXyI7F#~2}f(a{`5CJ2y<hqtB6_1QbP%>GeOa@dezUX(qoEZKx06+5?P(#CQY|oxO=ks;Eu@O9qz?G`z$)w9U*TQv;Ac~2E<bq<Zh)'
        'E`lBc$gs&RthlA}`kLcBkHa$4#I7Me()<qe&SMtBG?g?})n^oWU3}qLJEC10B1!J+^xPaHf(>5I6%f++~im%;lVE?Qwue2+4quNoknx$H<s~l1ZEo<R1$(^h'
        'yCF0JM5FFbYqMi>N#n8}V^T?Fb&%JaV*fC?=%jf?|#kUR*eaq;)*uI1q3=o=U{r9oq}^{ZG%lc4zxLZ{2QY4OhoC*PNp^&S}-8m@5HBR>LPAiA-'
        'D7WN&ZfTR%RysbhMTw2HxX1SewLkmarr#F*i(6-;=R0S*y`B&EwdKSt#<Aj_cQ`7H^z-'
        '3FRH`!*Ww=gYzre~$7#_c^d1f9bY5FU7n!y!Wo|2@@u;<HwI9n*|F)aAT@jBB8jW3?~`m39h;JBqt$xOj^bn<0kGhmm8*;<Q|xaapp+LRm;R|%`dlybnxVEx'
        '3^9ZInv73l>OCkrgA(2FB-DF%IK^}+jllKRL5$J6x<bV!ZKr+W|nDBbEA|paAQVmrDIxZDMRfzjt)a#%a~;zOBq>Wx==H0>N$+a!E^&=OfpV)-'
        'wg}gZAJyA$0h3LB<12y4HyFhS4-fLVCf~3E>Cz)8-'
        'TAYn#$9@4;6;BOew_^3B?`9@F3v{M@i1&j5|Vb&N$aha1w$EFu|l2@mP&k)pfy%fgu%%{`!CW@&hN9T$xdKJ$+RbVxeW$P;yp{J+Pu3kCi#AW*Wns*~@Z|+d'
        'KdBf&CRUB?n}6e|3u+IYUEURLVO#fRTbJ6ELkw8^b)!n9w|mv`n}va!AW_Ko)eN1|uK^OuYf^=tcCqAG~!&Hk(N<y8b`bUw!oy@yH{G)F=l#zQPfIVzedEGs'
        'FN;O*(Oj=dvjPzJ0PQ<WW>(wN^YH*W7jEoO30>9nKsf7<rr=!HID$!G!BDL3NE`&T#+OnrE|3x^&U3Z2Xd&R<vC(aq_IDl}pnioXE-OIAv=IEmffBSb!8y!h'
        'yv^?$h$l`|(^A{_gKD>V5l()2Fr_*^BjEylPWs;gpkESF=*@fM>Wi5(yOqzNUaQPjjWU;XGnma#uyd*OHT#u_W_KWTY<Wf`*AtYZd4{<u91qdPUN6CjxjrRd'
        'Hf?L7`*0*gs~%=Q!BhP?-T>MDQ%g10ecB#p7`Wr3`nR80TCH#z;6Z!5J~Zna8=*+#2i1#>S|(U{&zM6LaU(ikmLJa@G|~7f-'
        '3XU|t();u@;Z57PV4uH$(3Jr}{)5|&M`!6kD&kX0xOiR+3_qoc5kI<9S!X=$><6`S38q;k!(JM)Fjd)KeoJM7&bn>}@Fd%IM{-'
        'hmi5Qjx<|5GY|ouEMldx@<V-j+UB@fb>X9J_3@;5eFcQv2n`~2fzo5J|9<m+dtO_5&#Uj(gLvk1BK1;nA-'
        ';+XsLE%`%f0(IGzwf3Z4+0Gfxn>U@qr^TSvr_G+f>6_dNR0>_u7r?knE1WaZV@FJ%*JBe23rL(y)_0?BkbL&K^COWM0p7tiD5X$OHKSP(Q3(l*33<v#$EE=D'
        'E^ARIzfK4&hi8@88Tm`wHL)U}Uq9J=<YExR^t+3WtW>5_RHtE!4lrFSSU5>BXG!=0caLgEU(RYnspb4Lq7I*I}<s!0!q8UW&(cXqDL)~5FWaC54kvH<UX0p1'
        'xk5&+BpnCYHrLC{UZ!w@q&8uHz_;iFHj-CgjtBRCgaN=NX75S$6gTrPQ>3zylL*E~@jJ#Z}5a&Y5&-+J@KpZUb6-!S#cOByMa->JD8V7$J8a-'
        's$6daBJYH?inT59w%2cW9PPamBMc>e1RF(Y|65wuBNlv#nV7^M|7^J<7wwIhasX+f-'
        'vKOSZLfxE_++*Yi6Zx^iJnOTzlsAK84Uxw9npwa;lO1cSwdV1|eolVF?}V~SZJESR83SS}bd5s%6d#iVfVdvJ5^M|W;GS(}9D%Lm3Ja3*r2I4*~zKLy^IRHe'
        '2SvcG?1P@uj(?#5zqIs=b^%UDcsNRrGE9&7C=_1yo!MOV(t{=)}9di#_Mrg<nIUaQ@7oKw>@tUnC(i`Dt)cYCBcr5gxtH6S=a1@!e5$DGeTx|mIDZNjVmbrq'
        'h982)D0|FeJd6BQ1dY73<RRWx;~8&^;9=`AZ0a@7S1!OLC1v3&+i(a{qj{l{G=`kvWW_<F~ymOmX0^u<jWMOs@G2EGYHt;0}huE+$2bQn}3Uz2il7%4$I3Q4'
        'PwsR}C@QHCxM4Cf<lG;-UQQs8+91hQFhYe98&8Bt$fEs{yjT~|tYQg|+xQgQ+5I>PhZu(s6?AARUe?|A*nFMQ@--dx{o_UlU5ZkCvRAzOW-'
        'HhTYebHOK{OskE-EXt?bnOl`4Cz~d3auo|FwDHuG6q{A<rX$4(m~ic6v=#Rt*K^7~owxw0dcj0Ok`NvhV_CL6-'
        ';DoW<EzKkoQkS4Y0O$OTOd?at$X##YnCKM?d&U_`^}><x2<)n=eP_^GwBL~<-+w`r&P>~N-'
        '5ygNzZi{7$+ivfI}JrASomRxkO<^t_1}EbR6uABKe;HkAO2tay8E|C2FhT?(YG*bB=9k79JxmAYCa^(kVKwNv(hS!=L#08$R%!H_zq%_TQRVQ$6pmop1i;n_'
        'd1#9!jc1nMKU0u4PV!NX%?xY{dlvS6t%QMGJ(O)y_|5TIpuF3B8?l$X+oWGy5OFPcxTN@xlu^T`-5+dDA)CYZ-'
        'SUI8hPYO|xUpRJwajS#Ml>G+KD^Bv#ka%F9Rg*(ED4w3BAepSR}jhuUPE@0AtH@;xO-2T?57J;*1{oSA8#JTdw7_T$5pNSj!ku|yogW#EPcDQL0)fgF-fL=='
        'ELfP4$maj=&fp%^<L$wtbv8a}BmbWROh*4yh<-gd3qaZx*K{LVV>WFq4@+?CD{Jl%M3%cnp8#Sh)GY_`??TOVb$%U?|otgS@v{lQS!*|?0kX^$AISbIT-pd}'
        'XxG}aLqU`r8@*H#XNw$KN>)jmcOPWV)P>q_+Pe%yYce3MPpF{q3~HY11<a^x2d6s+C2RnvxD8Wk56-'
        'y(Hlo&M6TM!e@WP0rABkDzMOT(hw!%f9#d@Akdxrn=L~n9B+!pN4(6F!{2#r(`^7p8NHWp4_>9)Bdep?w+*+wwqOZ;mlfxB~3uXL!qiDiWDd9`(y%M)~p007'
        '!3U>rW=Of6Kj+1<^#pbrL(JRzVnvY9Sv3Dt-WQwaqd5szp!F)O?AF`a^8FLp}+my=id32tCnR{|F*|P?TQ=mPv1T2|I0Hq8nZ9qv7pbI1(P|ua=Ao9HQC4je'
        'Szh@%zA^&$b1DnpCem14R3fa{ovYR*4$c)xBPg>bb1RdOV%JvHbP~RHmW7k^@`bgNfZ;nP#Jd3I>pxPP?1wl(V^YuZIce*d!L%+`P-'
        'kQOv`k$Avb|NeeW;vz7JpNmnspDaVZnoB`62hmX1DY!md5#a&D-*^LYQ}-Fu2_9^4*mdB%5pXSJk-'
        '8{{!uqA22|1t%T&Wm9<xfaj>Mz8<2ZKJBdAlP|9QeA{Jno9QcqWvgo!Ts|@KYP;Y6#WkPa6lG4ZC!c!5XaD8xAG__U8r8q$aZ!8aYw)*UIpBY7>m=h&pU$BM'
        'EZuU2qzmS7Yc$XsSof4P@gCpG{-b11ZK2@!F4Dz8Lb-tAKoKkErVw)ok8I8(Q56Rq4^CqXWOkZG{VZdeX4+Cif`ZnFA?px10`}lhgS#J%nD3$7oijIOHsRNw'
        'pW{_FKSIfd4!bVbfoJahnSaCb`XRTvrM9Xu>y!)qQ7pw(x;6tT8JYY5uXJ^Wxg(t?w{GaZ_lpme?#(x5h8kE!7Ah2~h;+!vaG%V}j_YN!;1||q+=q4!4|aaL'
        '?Zb6R{`dQP^fzDgQ}5x8|9#_+J+7yH<`;+F_OtIkSoQJ0y5>6{ddG#Lf7^qoU4AWn^gmDd|GsaIi8VJelZ?Rbc&&?u8Zw0n+`~*KPAKbiZlYk<BP{4VPC>38'
        'CNi+bz*-B&4E#z2Sip-57{fq}gNVQcgGj{@n>59GGcUKgeVHk=B*>o<aaJ7%iWQh&{x%dx^R`sd_9l0Yz3X$+z0&#zsAlp-_O9m)e)gpw-nV$!#66xVx1?;@'
        'ZElFwwY8?2vmMRZ>WQrhudz{qfXd;$;_%u%yMFwuQ=k3XP;A@sl#b`i6h$E!#$fo%sqd2Ma30+j4EKDe?IX1*_K`<+tG8YDS?AGIRX)A{X#bYy4-'
        '_8$&JUg#di%8(eeIt<b#wK=^FOz>E3RSx_=8jamo{~n_=HxjV`cEaezS|}DzdqfP3&-V)xqP?8-L96tM6r{!^bJg7hzNct0TZF02<a9NJ$WaVDxDIY89-'
        '}Fh)ZM3PJa23Xg3gHn^9nc%2dDW)n!CY_&^l{%o#~>@#jf*<C|TbZFg1^_Dv>mHitZ#l@E|rDG*8`|IcT{ieTZ=EmKX`0j08eBGu4`Dc#pJhj0;cBEJLoJ_j'
        'RR3)d+)pZ>$*-5d1Ma=`lC!fs4kJZH@hZ(?f5PvE4Eu9W$^-koEeWU$NjT!b24{x_`yy?qo@6}g`tcaz=vD1}sTOUp@a4R49%;(;<EOGMpIyq$;e`p(z-'
        'g{46$7anJCJ})D^;=w|l4Nrgo7p0CYX52)eDps>apz7_egvz1z(jyGfCcQCgx^}&(Kfb%qBF-'
        '@!9v3*AnZ9!{?WB86_beT8QS+0GZ{f_!8~q`9W<_Su=Rwr>B4cl>Z%zczxgq9(UsT4*00{tgcy6S!Q)P<N*I<*ggqkN`{Z%CWz&Y-'
        'v+CIKJnK7BA8(r^n&!`Js117N_w72p_MoU4OmJTsqO-'
        'GP7z=M<7NQtObl>}0XU=Tl-`{jxeeBAAEv$d_%6PWl=a7=g=IQOGZ{vm;cieQ*C$G80qhPR;4b;rH*MH%3;Llhom>sa}-EVMFogws9Z0#<g#m<LV-vi&}s=o'
        'khLf9xc2i8cHWB@z1Vmbp9qt{2DiAH|7R<JNY#85i8l|(`kqnTF66d@yt=FH+|+ZHX7P4vX`UHbY3G1i<3xEJJ1X5vLH58wOP;riLr4@Z7U3Txq+NYurx!y8'
        'lT-=EHJym94)jg#ua<&m2ju5GQZkN0;vcWo)H$<{iYj5s?da!z^DG6{Uo9)$DS*+=}yZe8*ZosV3$B;GVwA}b}6F;B|Aa;Pt8kbm{sIsH-'
        '{Tw@apmeR++do1j3SjwF+XL0i?Ne$IxawXfiODeYe3D$T2e=*}5=%@s%q7fFxz*;@3Km!;9j6FZw#$L04HLzxMsLp7ppa83Z!oxpj`K^y|+AIz4Dp~7Eu-'
        '9EDS=eX7DVMPKeWxp+_W7vv9>L0sYcX%?q&FQqbSy?9ZWZUyf+Hkhd1&O+q)9f;n;3Kr#WtSaw7%lCOfntwvI{Ryge}9$H7+w^{G<}Kwu0UNJc3_-'
        'u)f1{*ow`^)sGqy4N0vfBZmtiNG2N6(a`37bFN&FzBHQ^hEJT%pWEiEpYLxnUOGl*eg|h4%;qXzLET|T+oN0A=?8wupbV5>7*QPT7;ttJkcPG9g=X|fJ9|x^'
        'eced2Xa7b3v|ogUh5W;h5gb{^X@_IjVA*0~GqbBMmN5}xU3n&c^83CpHFYMF13UE%H!hn{JalZ4Q(aRwhB0sfBF>Z{Gksc}_rAaT<vp*u?e32cob2y{3aDmc'
        'YvaXjn9*B_l*_@{_$a(24Gti@bh>+)vUce5&kb#^o8Y7ZYsqDtd)$#F#PnpheB*UXsu`HHsGo#?xo04<&9fL|CD5x@NUb#z$Cyr@JZ1YH`5xz`B6L^=VWiXJ'
        '6=to4HTDIi8GT;$jVSiTO10L22v9)<@O{YDKY-'
        'tLiitfi2qMt3#lmJdSaTcu;-f({?6lf2-%CpuHe*_Q_UaR-x+OS=VT>R~#;JrW^|aP{r)Fk@pU(%!P%3h-rdGB#%89;j$p}m1C!JX#Ibzo7IG-Oz_7EV#rlf'
        'LQS8yRnCaN6MyXR<j;bd=Bdy4~G+rqc*4fJE(P1co$%!N}K8Zw~MfvxE@rhmiT!kjt@t-~>Dv*&c&nz5=H4{sFKxNCM4`q<ALQKChpBd}Z-'
        'X!EZq>a@g91;!=>u=E1q*s?vWJLrM6`N(U`vP^W+F28K?oWAXQr-*bWG=?*4Ia$WZT99Shkgu%kF%N>1QIV|#CUD24Ed+pC0aAJdBm-'
        'K?5uE}oISv;@T5wL%t4>Gp;l7J5otLfxCqs2D`0-'
        'PP$W~8eJZ8a`ED}1@$n*+hyLPeSj`akxFe*CR$upg{V}r#xU|uj;JI<`nr`&UWqXlUN1wigwi>PZS!*OY;6oMAa6I353)Mn`?&jw0oS`qahFjp+^VD-'
        'u5Vqa5ajA7savz(a2DG*Xmj;pHrhSU_qQ&G8ZAn3~Jlc^MlDY9dO2#XrQ{4m1+a7(btS^~7-'
        'lFLk7x@nht`Ml=sX|wpkX>lNyw8MGV{$`IbEas7&k|o<vO?)7*=^@zuUC%Qr<e{SwL>TR?9S8D^IgSVP5+;21b#@#?`@%5+Mn`~O2H*8C^y!FrcW987uydwx'
        'Aq_p#TV?m0BF!DiCe$;`m_BJi_rb#nCnh;3E;U(3#<Ggx(Tr-<R^3$70^yocu5V~d4-VCNQdATS8>>EJKs?YKz(}5Gk;-'
        'I}aSJ!G`Cyr^J6JZyj}10Vte5kvQw&Hqu<gep-K87Jks6peMHmLe`j`p3yC^uYnZ`Q&a|U(KoEr;^@k%;lwqx2D(6DACb-'
        '~!w=Y{mgS_85M$^zop4yfKkM7`1?GN5T4LV6aFo2BRW2U^rNk|>_QoY|8m_nzo$KHBF*8xI%lVBolnlQVRx%r9FIzacYinxh8#SkIxJ{hRahbWB)gHR-'
        'd9exgP&rNFskIRM!=Y>sR2>BGZFbe%e${MvilZ@BA|Q*Uk<JUpYO#%oYuK&*<^?DI98YVazTFlho~<p@y^NB6;9oDcRu8#|i1jZ@5-PQ$zi-'
        '1$vdpT~U1_`fj;_?djsSPc}1LB}_e=_k-'
        '|Xwlq6)KpDy6SU?)q^(zjppdhZI@;WsP4SCAa%1wcuiephQ;X`V`t3gMFRrO9nZ0E46{5a1?BBVw^5`@Dcgwa+gkp#ijZABb+FCH*2am;)l87hZH9M;h;Ly^'
        '^!Og$^eDm#>zxs~X3{ALU)_<20>OI+e3eyiiEDEInB1qu5LnX@{LAE9dq~c)x6|3_^=-CIT2-'
        'a$l#kn(r=a}+X^Bbc~JAVF#jjE17FPh^SX_oA0r81gq8v{!WtoHy+zCwIhSY5-&)>kv`^qXy6gq~6itWcmCHQo5e=ihioH2-'
        'z_r~Q)Oa?zu&x_R{jkHz{6i~P2E)OYMeeEV|;?*HM*#MY_xDmJVr3RP%DQ&Tdowc#zb#>s_M&XYTbc}q=KL)(-'
        'Eld{W~wzbZB(?8n8Qk*oXJYGWd)cgh2%cj2$H}>3xS;gb%9R#!{GN~97q=3A(y5NK5j=@-rn%mg&?1crTFH+6es0uS~t*Hfwje@kGQJ614v*)-'
        '8OBQ5Dkh6hKsNo!me6!(N!B!<nhlYAe+!p$}P3z3%tlV-PsO}0nsbQZkp!|oni&|ISe*HVH>HQ5-=0xT2A2xJ<@|VNE&L>-3!-'
        'hnt1R^FG_Xw?hgC>?6l+KLWzQ#NMZSiaV;h*05sR^q-'
        'cvErGdqm!8Ga9hvpu{&6eOXb04kAlWRjtBtZvt+bTI4PMVH~dOpuy~9=Jxp39P20A^$6KgVZ?8p?cA91Y-'
        '~z19_Dy>=ULuFM59wW1Uh?>jk$j2n1jK<PFw)lSZ@m%Vj|arTgp${ue_<rnQ+l-'
        'SYh(JQHf86wFZIl`KD4R3jsI#D2peOD{;zgleIMoebdEUu_OEX?%AXZC9Q?26c}A~#o|}BG|0>~3&Mq$th(-'
        'X={Yw~u6XlM0>JG^sU*SCrviMkTcazA!6OA@fg*E|5Wr=@dQ9!#h>cW(-yB$I1~>On@`?XPQN9SPqfyh;FPNzrb8Pilzjrp`zU(9`1Bio&jU-'
        '#dK*UF{j|_R8Jthut0mtDeE_=6)En8%-'
        'o419%*X_chiL>EXtv~?+H0p~T2=qpQ{`)Rt`>iWnXc!CRt+bMZF2NxzJNetw&V~mccw)`a>V7m8sPo8^dt$uQ63FT_8WuuPOi31j0}SA>u;hYK7b5%Z0fUG<'
        ';xsZX%3u*FpvVbT0=S^K4O9E};dA$u@a#{23!#e8N}UVPj7>@On7}b6Nc>TNYy=>2fQ>mO24Z85iGc|Tr7d3f{<qqXzHT~oR2jH67bB0@NZAJs0)qh{K{ypw'
        '%(n(DSUka?EDT7KHP%{d^O_s3BWFQ*C%qQOiWKMr!t-Q<D-'
        '!7k_w#7u*1<x;%bTQY1Tg`twd1fT#w<*fWHh+7%M|w)m`rdYO8^0(wkQPxJys&tp2w193RSLxv47FK3;wJnWyTO%Qb2o#;gREUY}{vHDt$J=0;D~V<OFLJ{I'
        'UV7cd4?o2gQBEFoKNIOmhYcGPY8&rc}~?yuBQguZ<^#=V!z}eD*&+JgJe_O{yDMys+i6S3O_2H1o7SrRdm-sC9}ScN|24W{Fy^p4>7R^*+<-'
        'AtOeV5=tQAm^Gmfw=U|2nqH5acP=xBI!l!F9-ydrz8=w-'
        ';QGH=AWCE2LNB>^R$CzMF?@N0hyV7f&F!<EV{=N+VRvB;o*L>v(zU2@eHf)NTmqVi;khlnbolWui<DzvEy3p&ipkdY62EQE{$Qcr{?M;}<UH1|TKmK=et!49'
        'd<6t}>;L&p+a7wy^&4);H7>hsW3V8-N6#Q@t#ME`F-fRTK@O&+HLgP{l336&fHz)r9NPA&dnQ~-n_FMaJwLKubr%^g1u7OtSP_7+iX0D-'
        '#+2ihUglN~dg1kSo;8y6Vvq!aaXh$n&B#}^*ss^T0UiD8&Fhc+#(ZE}8{f|^#{O_JKoQbT0LO$@2&QDUhlqI^n#rXX49i<)94;<t+W&Otp>22F{)wYIfhYuE'
        'L`z+DWwK|52SZ<ZLLK<0U;OS{PyXHdwh!NYWz8Nvi&mEw^QTMGD}i?WyicjH?6CQhD){RQH{zzby}08}8$6!7z|yKXPcD(1r8R|#8f#-'
        '2BI+6Cah}z*G#1!MB(-'
        '3pu+4cO(y0GC&kEhMk@v;wBm&^2U{g)tDMrb(#ED|Uet!KlJ$=(I{m>oToLp)e{l2gQn=5Syg49r7#ighys+P<z$~Vl}n_pDF`{5m%xBX`M-<{k8xc-'
        '#3n1x9NA!k~^ltKy}BV22%QbPUf0(srU3uny<5)FR!>YtUC((gB1IOVEE&w5u@h1m-'
        'K=q=B&RTFlh&FO<lEk`A&7#^4K{Ib=|flWumQfaH}+95jkkE9bYuwzmVI~E$9XQ?%f8GXh$rJfBSBj-ftS&2d~d^Q0v)mgAiqcv%Qb{xoJ-'
        'dc}YzW^)J^_bQD5SpSVG2dI}Z?Afd6SNG)ufBC-@sf%AAAS0%&G%gL!>*k`($4BgM>>qk-NSjGb7&fb<;``xE+sgRlCGXw7^r*C>nDAz<JDJI>0`U(@9*39n'
        '|Iz7{Ip?s!}gW6N1|1&NA?|l{=p5W4)x8ua7uz@+Os&+OJ+@Hoe>F6m^)qAm>}NEjT-'
        '1@{OD$wvt`>Kzsriwk<AN`&VV}y9!Am_!q{|%omJ_XXe=0mp0NyK<`QG4f<X#m&u>#fXUVS0cGF*7AtdEa*r(U^(y#9N!}s61pl{FO<c{NAyC47N>p!vM0hM'
        'm{KmERo8c&?;?8@bJ5v8)PC6qe=l>?MWIxfXr!*-'
        'lfmG>`mE^EDD`V<DGdUozV_J>2b|E9$;vGsK9^uzzL{Z8Qudvv%){ME#s>yxgnM>vEPGn?4It<P&S7_&IpscB9Jr@9KLd7iaZ^~CynN77<?;TAWtBg@v#lw~'
        'itM>`79y!ci(8tX65z#Hd3$NESBj4>dVfNft0Rs*Oim(bg9(KTQZR_vuyIU`$wD-'
        '?B|_M<I>HCx{JnGJ`EJ$<OI&)V8rGw_oyUi$vl)~eTT*wne~zwX`<Or8ulN1(e$mi`*1jb(5gWXt*Zy!mxkBqmJO!O6q!{sTjQ=uT%&J2o^88H5X`Rblp|l)'
        'UVc#{7v~w7XC;z;MnioGf^??Xh9VEcP7K0ALz46ZLIIO<o92fF(Z0)Yw@yomI<=uJKV-'
        '@fRP{Sa@STV~kpf7%T`J1l=+nylJLELr8EL?13XXDjBd!uU#?26&UKZMgd29{G&~6>7xs$r^F=}HS5`J@caA2Jd@IA#6+SdW&vm^&s|f^JZ^c>GPR@uP1P-'
        'RlMqkXfg>jdp50S<z9~skMcN1$t*wrfLR6EK(aD0?yz^)Us0`cs8qKcls4(Me(4mtC10|RSk9Z?sW?cm&tH8JbEMDxp&H=#AsV>fdI_I1SM0^}@I>&TDY~;I'
        'y1UU}W+^Zq#<5p)SL)n0K9Wap=_QINenm0vq4Cl;=o(KoJ)RxBf#^Fj{MTLs;LyHiA=0pb8z;l%WVBDc|rwf^spx(hy&uYQMWPNQKk<a_P29NLP=bdqGgfV2'
        'b2FPe@nK7u8ydYDvb<K`^8Om@w+=F+lOiB!#Fea~HH*JaF3D^mWoQA17oOLNA0hWsw`LuH(zTn4bv<!RE@t890TzKc!!j>^eBB;p=AlfcA)E<(_xWJx$hB}9'
        '=9n9HxT*A1p!+;9t*`0ZGhwd7Od=?lRA<`-ewF00M3DImpg{~8&5&#Uya|R+uMx+Z7nM@oR?!`D%!~#DYE-L0T3$jKVB5k1nGO&KW<h0M9(7EYwu<rEf2-'
        'I`JTsl7?E=rw1Xk1|ZPL06|RMumn%>wgZV|8OYq>v*XZgfOtEJPyqB9LcInfQyZj}IDn;oMq4NEbF)1%2@w;50c_O^}QN3;XP*D5NABql5Og%WEV$51X)TY0'
        'b{UK0ayU_CjyoQOZVv;kvii52sA2iN#zwKT>A@&+pqeblI$WcIwob5!_LS6h*LgNr#;{jpLR6fePH1PFKZSTRoi)<%kzIMq5MLN*Wm*t#YkA873Znc>OR?DM'
        'A)b;ZrxJ9DC}pfiGd6TNjZOP&2^1=0+1;{%(-#fxEGh#l>tqq;clU&IgUZNTp}ZmW|ZF)&k6pgE2z5;w|vnW@<fKGsIoktvfaAE<@!`n-'
        '8xrye?fNln3m_Jtf-KW$$aBTw5%K+9+kBSd2{9iJ`(*K5^w#*I{$=!<7dC=!V(#7=M#Dvzl~0Gh%(eIC^sLiFF7}SUb73ZBDX0=iw($<V9rUi2AgJRv^+g7#'
        'L2ZJL>j6a}c{L6K-II1AEQQ%QNz-h9mHO0()kgvImbFQxzvWFJf-ng*v$M-4Fx_H-1)$GzP%A<~zEOXcWxIqN4HO*f}FJBk*F7Mj>2!8=UE{HZ&_B-'
        '4G|_hAbX>I`WagRJFr?@U_j3Ik?Lh#n^A3?e8trwmuPb_j|@542;&CGt*ZtmzFPSeyy<>es0}~M*+ySYxCo8x&d#<pe823H|Cw<^4RdCiBqeVx)Y{^Gbbk&U'
        '31-~?AyQHvAH!Hccdk*jAfRHMWGhe^|f~Q_CtL&*=d(AnALzv=N?+JbUORVeTO2|IET}L-G(lhBTSV?JQafUWE-ZcNgm$`W=C=WvUWs`XY)UHZe?*!a2P#j^'
        'g<+Nd?aCJ48n;)Fha2WcJPaCw|qW9O>!BLfcg175i2-'
        '|4sFwSzT1&A)4iN>N6ZuJ3+%t1E_|bP`TPxquAGc2Cdec?o_OLw?&*8qw0!3DhOZ6|mA|_1nxEWz<I>v1#@)Tq_?vBbwoX(5no`Mx9XMI&o>f~}R5zuyAvNv'
        '7SXFT960v7jZu3cYWH_EI#~j9?jbvPk;y}Su>3G+X4LjOaTz|s^*1grVO|IoNQsMq}744*(m^psHu=%sO$p{iDWqCB+1oaab%N>BIlwi4lwWAp!jm_)EC($p'
        '!qtPL&vz3N);4ls(GYD3_3(mY-44+R>lO0A<!u;m<kvQ0I%e@2UL$eRk2X3u(^IM-cY{sqpi{Ib4`$)R^tDYZ-N~nUWDvrk=-'
        'P`x~A6ilU_Set7I|}sf&;Qr<_xXN>AL?>UKA$%)R$xkGf{1K_`{EE!4pt82_DpaG7p0oh)x4&@G_B2Dx*#z$rFtlbQzy#Bp}^7Ic|UA#Z%t2_Ffp}$+pcXxr'
        '%RV!cl(X;-'
        '1EP)mtDVD9Nn=`ZR)A9USvrh*=N}Nx!hzV@pJ%b+D+JeAsJgDIn)DYG%WFvviMAacQ&mVcMO6ZHCx6d1n1z=fttDyYSjneO<k(lJVk1v%gB*1_dFQ!4F^>@l'
        'vwKj!TjR0vt#+S529+p)%M4~J#N2$@AIGLEv=mi1Wt-0di;?+-9P;I8z=nDJ1+PcBa*A1>%8qfAGxo0PJKdbJJ_wyGgNMQG9go>2-?EbIFWqJPoFaT`gXR-'
        '+{~I<r@eaq!l-3VN87YXiDehI;gXr&@Z8x|V#+OVykpg(d9xQw6&!!^-'
        'X}YGy6J)?OJ~vWu4m|$+n0*n>vpJ}m3DY#1%2X>VRL43QyU}HhvXt<Y~5mnEi(uRAu7Y*Q3!S>Sd0b?#yJ?{u*5)|gBS;A41zJRcmjITTtv&?3cm1m<4tTZ='
        '0e3(TbvOSFu(bI#5NpM6_KF@gHM<T|7}K$4nD(D4O7gz<7xiS|NMjRU;CD;ch0M&wqM@A=j4(7UBg=+f7f+au9)~E#!!6XnPacL`i*xUShT1nwq{G8I?pWDh'
        '}UVai)UTWGRIgZq~)oYbxzt?IK5PAc;^y%^OBVl-_S5`daGOCtTYq0QYcx!WSFd9!mSnN__KEv^w6=v``7d~FTU;FiEBDe+2QU(6kB|Qech*b`M=9AqIhEs>'
        '0|_U`?V4iS{Q-'
        '|{8V6YTtJ^zBlEV$HxcXE4>s5dl!igdN2#I!OGw5TjPw961yh}cX_x{#VIg>SrV({9OYIS<36df10=WTe?*4tqyGpiPCVRo~Q|8ex&x|EI*D+zZ>8rk!z2j~'
        'F_DpKQ?63alZ!i9~BU$p^rw)I5*|G^Mo3qIqh6eqwT=9k<eP!p);c(%?YO#6qVEDr1^Y}G)05vtCK4!qQi8IHwTx!cR2`eMdwVMxz(YrgM88<9WTs>)8&GJl'
        'h?PRZ}E=ln?6X_-f;o2}NDrJNboWdXdaBXVkwb$~6RfkMzu#35KSK2#1x6}Vs*Bm$<(-{x@tX*}npk<4MO-'
        'N8F0`CqD^>S<a8BC!}W++Eg>_Kq43vZZNL^cV0bwdnpT^2Ug1eR&EJe{zt2CxkgnXF_c?SewUZr!f%;4_h>GzHzgW|>-'
        'RfAjxl$5K6;7`MXYsxM<7{Ohl*|Lx|}@B865Uc2ILS55c|cO>_%K{1TBt=-)9u^ZoV*P7PWbh4I{IUNp%-'
        'Q6&wx4fG3>{SD5&!AcvFp~gtb)0*iWn5VimsX@Qjy!2Rb?8vu%=LnrS51{uCO6Be&5g0CRn@Z9i#yd$B33tX;ewWAI>ipGTi^GsUmT0S^AqonU)*xq3?A9es'
        'xP@3U%T^U@X6nMI_y}&<2-_`CfKD5I4zhfkamFxpy7&T!`9NU1r-'
        '%cZU9fNIz=<;1kJiTV}`3*Eu|RQG=t3$nJSmyGN7zs_w3VHvq@2J#Z(X{9Neluys(FT;RDk=z58j3B{KSuS%7bR;RmJb-n#6*MT;i2GOHFd15+-m1A9*l-'
        't(T1KX%XI!?~el%O=Nn?8ucouMp&N(C2}7F2I@^q^$*|3|OSWV+k-v$GLJXm(ubKcVs$dgfAWHiOBX9EP0W3<HWs&6w-QVIQh$;-'
        '|>+|BG&MapS}O9hG}#i?s@B{{`tMjmR*=OgPVU()fX<N&8HIT!{6-+pDoQKWZPLBC2JevWM@t0G-C=wwuvFe!IVa+pm593BY15jv1;Z-'
        'eC^N%d@1!hBr^h9IzVWF-kh}uk7(L;NTYMm`jmvt<;;v|yZzc7wazscOF6vh8Dz3k%-'
        '(1g`~AHS;MO<JFHY*nmU6kmk%2<6`44MPtbXrj9^Z~aSOQ?~{@xoeXl<&AExGAGA6~R*irlc_P;eg8J!f2wvOrwbgK0g|QWi`nz&xGcjy7DlmJ4Y)6Rt>kMh'
        'X&=Ji*BkTo4yI-|*@<Po@)|(^b@!`uYq(0Qq&>-t+c%-E`}l-'
        '@F|Do`<!FOHS?c@smdf!>>IWsQtQwP?IG`S`wZGvKg|CHAJZdGoC|VPOo9d=vI96iizmm^IcrIcZR8$xWRDVQf|=L?m??d2BDG`gE`wA9klOVZo~&}ZF17X`'
        '>A;9lu6IOjy>}9NqqIocRh8-$5#Emrm<o0zkj`R|DAVk?E(TH0G~d;QB10-<LkHW?py!6kAJ8-<F(h%|J-'
        '}8zIsaRkw*^sV*s9aiz(3!8028HfKl~eWeujwU}Q?Rl7NY+gm$>$jvuLE<tUag5ibPX<Az&@%W7$46mUHdY2K7{g)ZhfcO6l?^3rd7^Si&>yKncA4}RcpUzc'
        'w2a;C6z4c@(Ef^+-jZSwxL-O<mUJEouMsxoD_iO{bJ`v(DK&8qBSqRVH?Q%FKt(5y)p;krA2qJMsHh9;L;8xi1_EmeB#;+lSX%PPiiT~Q;mP9H1m`-'
        '4TpByFeOz`yvF2i33c-'
        'teEn;w3+O^Jn(>=y}RC&#lGc744psTo#Iz&>t#>1Eqis4kB_LE(K>U0PEzr9e1O(eW}gI3;^l|2szkB!18(+U&H7Mn6M>QVKA<a^Wwm;F&4V5AtM4;lV_MxW'
        'J8xh2u`9HY3?}SDlmed?)9czd-=l;uim(C-'
        '#h>HuWo<Sbt`VT`DW<cX5)4~hquhnI&WOogk4=)uibx4uQ{m9jxN|ELyo=S3hAs5E+EGVEVM#7HXrY}youkxWw&b7#?ERoblFtSm(Otdg&j45=|Pwin~aGyX'
        'm`dn{E6pJ@}K?aTU(#mm-~9-b+>F0-3MYzX2(3tofJi-AS(8k!-'
        '`dr)S((0@|Eir0Dz939C*H|F1a6oF*Qm3QhsmzG?zHvHg$~vGxZ>?!IDYv!9lQBt(cpsOFPcJ_ifHMHCJ<^M^Yb;OTl7-6EnhfV_Zru$l)A-'
        '>sHm6d}wLl`3=jL%xi!94L2{Jy5zzvYGfXE_=F}zj8#_?VzoG3N!Y>Dy>>TUOy3>6jTY2J_{gd(0_Gx}dlKDizh`QiS}9wj2(|<a^jZ}93`%)ca;MP7To%9k'
        '^`o6nu08&v!HH8JoH(`3FLif1%px#>QQ9b7@wL)AQfJ^v$yK31hVx;wbnY~#z9CLOzI$6?G<fK7(9R2xpJ%21*>!_ifSMOp%gvhyE1Mts&@ELdr@3Rrm%qRC'
        'g0{@iK);E!<wCeZNXxyL6pRZ_t`IKcoVkJ<E~UpwipFekWbd&QKYnECypFo-FIhbOq7|3UVI8e;#Hk27bixew_Y-fNKwm6>42R0~m{G^^!IdrW!69vg>Mb8Z'
        '<?trd#IylvW+IDYJrUOI$Yafp{LW4L3-|R@H9pn8Y*CK&bb1xPVn`#@Mr-'
        '41rF5jVRw^olDhMiCO0G&Ju7w!XLcolsEN0xD>3`IO#}lSe@^r?urzNut7>p8e$8kI_1|YOLR6`Nho;D`rp>`^ktBABnF;3cO%M~Z11!GKWmq+|~muzm#l<n'
        '+SKeXj&?(ucMSUdgh-#))=T1WH6(`HPV){%ANlf3~9*ItK%r6#y2!RYwNqAVDM<RWaj3Z2hAiRZdBJJwYS4tMzn_jE=Z4(Hux@)M@-'
        'n0V8q^5m|g@$l$DH(&^OptUwiTcflthuY{!MIqBp=qn?+J_FBnp-0F0?8~Jre+-'
        '}<vm3?OXX@<S69I4@d3x{a>Qur5Aamu&_x%EdhEY7l_!*Es<3fbmT8DFM73U!*%LV5mVtJpVa#Ykgo^@BP+%e$9w?4A_Q0%D(H?{Y6nF-'
        '(d)WSC%^jFNwS4`v*6UD$n8OtnVWC4SwE2%d&<K#QO_1O2~^|c3vQ|*VFFK8>aia<oU(_VCFS3HDKI?&o0r31~i(poE}G&hlsBCeyTqTp~{Dljt+o_UFK&Hk'
        '~Si(YO`g&o;5W+c!&vid;rzQ=YC0ic0_im9r=hH2O+3ayCZR&lc2S2ncT7{jc!p#@-'
        'kZLKyiTEjqdZFQt8#S(LehMZJN5NakCmd$qtu6oVQH~xC?)iGDHO2A@aO(GUvH8tTl#F>C54UcBD0YkYBKiXMoJwB!0XRNQ^@drvQ^p%3rQ51$MilD<tD;D}'
        'n2Ne}ntRnJN7;056bFCCNjx(rFpN7fjUl!i~Xz#3-0%|V145+IEMty}X0=8U+t*U|zDL4;E&seK02RBhAvd}PO0uyL!VPGOs%Hf19YkQ-AfA8eiJYW6BR~=y'
        '!hdnQ1ku}y!FjJR};Y4K2pfM^WiYiV+tkvvfU;pOXXIop7CM>H!kyWJ5g403dEAp+bR6<20R2Wv2wOp6WLUTT3T(_codS23G?Vqz<sCb!uM=@@<9;{w{HlaK'
        'xVt03s{E%!GtfGdEs#J4fj8WWY+&3olxHg_)CWx3Z4%bpK3&U*W5JL!*^VUsBf9HlCzG274q;vyO?DN@zY1QWb*(>P}W#Tm)CbUe=k!0`SJd{y6jLH^4Xd<C'
        'Q9WXLMSg|7FS_hG_jF~73wAN(GWv)5rMu-7(o?!7mhW9_&d<-x51;rw4xeR17zKvL5!Z3kyM27RoYF}B-T^j`2aI1~-'
        'g^m!KO5_{qCS~sA!Ooi&R9*S&_05ezA+V~XcypCYGp_95Cn6?eFs#V9^X9?3D?7jYA76O7uemSHE55J8P{C^WWvwb!0agcrudUU(T;|#sp`;wrj#JUSy)eb%'
        'pA=>PWE1{#Hefv8uDN#HP>%tidwZdBIcUcjRE{&Od|yVD3Xh`5kD|zrbUui*9*R^kiu_Rf&2=`o>#4A(Benk*H(%Tb9eD;0Sukb|$iiq_fK(SdIhuaxq5D7i'
        'E4_C{Ls<=nC0`YzNEM?<=YzAKU#alO_hlr+u#$2>=W@{FMpa%Bc>mKKEdOkft~;O{XIPcXLixUo`h5{a5s#D#!e}^%1_lO-_4OI^<)3VM;I-'
        '3tAMs+wfj+yM#)7P|9AahfgM}yVU45sUu8xAipr{IA7)5@hbrAOZBJzD1mCHgo&Iq{ve(2ubv(WU*jqCln!Q++Kg!X*@we!K$-'
        'QCc+9MlNNLFG8ZQKcfIN=2wjg-1g}GH9(am3yBqbauFVes;sW9)^-Mf-D#e3XtX^C&#8Ad-%7X_(gHolr|mq<W=R2(#mC_gcw$iGpJm5K;?30!KrZ-'
        '#Vew^S8^k6d%j?Ep4W^GHX{{Iwx5iFF(Y@X;z&=%*4Ea>zy9M5zq{>Cv)_F0`r64_Tc509AUG>~9>}l0=gFVPY9~a)!`;5)<fD-VM6is(j()a%nOyD_1@}sC'
        '#BI-G;&xnFWX711?(RNo;wqPe9v&VJC)NhxovX`T)02CCx@vAW8!W+=4L1u#H=B9vk$XS-'
        '^MTz{TZYuBQ+Yp^8&P#{FI0E;S(Tm7OwIo$%Kl&OWNu#u<avGMSfBvZ<^#n_eY~E1^JiP{zjey)BPm&ql>#F#?fP9|?XREuMLa&i2A#c?F{Wu=!oU5o-'
        '0l_I4*r$i3jR+4`BKWX0918rMg8!Rpubja|JgOOb2O`RP`2)S=-'
        '&7IqW@rHW5w?8NAwc!{ZsNf`$~8AF9Gm;;9kzW$HK5GCnL|Z?12s9x%b^vHTc%V5ga+<J_*mWv6vH`?>&FSO#dR_{x1OHPw2>t6vJxC5|Nh4_K;Y7yNT@PAU'
        '>@K-#1e7KL+go1lrig{|DvG4-u0A3p)S+002ovPDHLkV1jq5wlV'
    )
    return _zlib.decompress(_b64.b85decode(payload))

class _DashboardAuraHorizontal(QFrame):
    """HUD Aura Horizontal 2.0: uma composicao vetorial unica, sem raster.

    Recebe como fontes os mesmos QLabel/QProgressBar que o controlador ja
    atualiza. Desenha o nivel, a barra e os valores em coordenadas comuns,
    evitando o deslocamento artificial dos elementos no layout Qt.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.aura_badge = None
        self.aura_level = None
        self.aura_xp = None
        self.aura_bar = None
        # A ornamentacao e um PNG com canal alpha; os valores nunca ficam na imagem.
        # Ler uma unica vez; a renderizacao QPainter faz somente o downscale suave.
        self._crystal_pixmap = QPixmap()
        try:
            if not self._crystal_pixmap.loadFromData(_crystal_option4_png(), "PNG"):
                self._crystal_pixmap = QPixmap()
        except Exception:
            self._crystal_pixmap = QPixmap()
        self.setToolTip("Experiencia do personagem; progresso ate o proximo nivel")
        self.setAccessibleName("Experiencia e nivel atual do personagem")
        # QLabel nao tem sinal textChanged. Atualizacao visual leve, apenas
        # enquanto o HUD esta visivel; os dados continuam no motor original.
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(250)
        self._refresh_timer.timeout.connect(self._refresh_if_changed)
        self._last_values = None

    def bind_sources(self, badge, level, xp, bar):
        self.aura_badge = badge
        self.aura_level = level
        self.aura_xp = xp
        self.aura_bar = bar
        # Atualizacoes de progresso disparam repaint sem esperar o timer.
        bar.valueChanged.connect(self._progress_changed)
        self._last_values = None
        self.update()

    def _progress_changed(self, _value):
        self._refresh_if_changed()
        self.update()

    def _refresh_if_changed(self):
        b, level, xp, bar = (self.aura_badge, self.aura_level,
                             self.aura_xp, self.aura_bar)
        if b is None or level is None or xp is None or bar is None:
            return
        values = (b.text(), level.text(), xp.text(), bar.value(),
                  bar.minimum(), bar.maximum())
        if values != self._last_values:
            self._last_values = values
            self.update()

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh_timer.start()
        self._refresh_if_changed()

    def hideEvent(self, event):
        self._refresh_timer.stop()
        super().hideEvent(event)

    @staticmethod
    def _star(p, cx, cy, size):
        path = QPainterPath()
        path.moveTo(cx, cy - size)
        path.lineTo(cx + size * .30, cy - size * .28)
        path.lineTo(cx + size, cy)
        path.lineTo(cx + size * .30, cy + size * .28)
        path.lineTo(cx, cy + size)
        path.lineTo(cx - size * .30, cy + size * .28)
        path.lineTo(cx - size, cy)
        path.lineTo(cx - size * .30, cy - size * .28)
        path.closeSubpath()
        p.setPen(QPen(QColor(255, 230, 132, 210), .7))
        p.setBrush(QColor(255, 215, 88, 245))
        p.drawPath(path)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 252, 225, 250))
        p.drawEllipse(QPointF(cx, cy), max(0.8, size * .14),
                      max(0.8, size * .14))

    def paintEvent(self, event):
        super().paintEvent(event)
        b, level, xp, bar = (self.aura_badge, self.aura_level,
                             self.aura_xp, self.aura_bar)
        if b is None or level is None or xp is None or bar is None:
            return
        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        # Referencia 270 x 80, escalonada proporcionalmente em telas menores.
        painter.scale(w / 270.0, h / 80.0)

        # Composicao geometrica: centro do nivel (40,39), texto inicia X=88,
        # barra (90,54,106,9). Nenhum spacer ou move() independente.
        cx, cy = 40., 38.5
        # Vidro em degradê SEM retangulo visivel, necessario ao contraste
        # sobre os pontos claros do cerebro holografico.
        glass = QLinearGradient(50, 20, 233, 53)
        glass.setColorAt(0.0, QColor(3, 17, 37, 80))
        glass.setColorAt(0.28, QColor(3, 15, 35, 158))
        glass.setColorAt(0.75, QColor(4, 18, 38, 112))
        glass.setColorAt(1.0, QColor(5, 20, 37, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glass))
        painter.drawRoundedRect(QRectF(51, 9, 182, 60), 27, 27)

        # Cristal Energetico (Op. 4): arte real RGBA sobreposta ao fundo animado.
        # A imagem ocupa apenas os 80x80 do circulo. Nenhum deslocamento dos
        # textos, barra ou do HUD completo. Numero e XP permanecem dinamicos.
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        if not self._crystal_pixmap.isNull():
            painter.drawPixmap(QRectF(0, 0, 80, 80), self._crystal_pixmap,
                               QRectF(self._crystal_pixmap.rect()))
        else:
            # Contingencia se o decodificador PNG do Qt falhar.
            painter.setPen(QPen(QColor('#02D6FA'), 6))
            painter.setBrush(QColor(2, 15, 35, 230))
            painter.drawEllipse(QRectF(cx-25, cy-25, 50, 50))

        # Nivel dinamico menor, centralizado e com tipografia de HUD.
        # Bahnschrift e nativa no Windows 10/11; o Qt fornece fallback
        # quando a familia nao esta instalada. Nenhuma outra geometria muda.
        badge_number = b.text().strip() or '1'
        font = QFont('Bahnschrift', 16)
        font.setWeight(QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.setPen(QColor(1, 10, 26, 190))
        painter.drawText(QRectF(16, 18.2, 49, 46), Qt.AlignCenter,
                         badge_number)
        painter.setPen(QColor('#FFF2DC'))
        painter.drawText(QRectF(15, 17, 49, 46), Qt.AlignCenter,
                         badge_number)


        # Linha dourada/ciano integrada ao circulo e à barra.
        painter.setPen(QPen(QColor(244, 166, 48, 38), 7,
                            Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(QPointF(61, 63), QPointF(222, 63))
        beam = QLinearGradient(61, 63, 223, 63)
        beam.setColorAt(0.0, QColor(255, 197, 68, 220))
        beam.setColorAt(0.30, QColor(255, 219, 122, 220))
        beam.setColorAt(0.65, QColor(12, 208, 250, 165))
        beam.setColorAt(1.0, QColor(255, 209, 94, 225))
        painter.setPen(QPen(QBrush(beam), 1.75,
                            Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(QPointF(61, 63), QPointF(221, 63))
        self._star(painter, 218, 63, 5.6)

        # Texto nativo alimentado pelos mesmos QLabels do motor original.
        title_font = QFont('Segoe UI', 11)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.setPen(QColor(0, 7, 19, 220))
        painter.drawText(QRectF(89, 11, 161, 21), Qt.AlignLeft | Qt.AlignVCenter,
                         level.text())
        painter.setPen(QColor('#FFFFFF'))
        painter.drawText(QRectF(88, 10, 161, 21), Qt.AlignLeft | Qt.AlignVCenter,
                         level.text())
        xp_font = QFont('Segoe UI', 9)
        painter.setFont(xp_font)
        painter.setPen(QColor(0, 5, 14, 200))
        painter.drawText(QRectF(89, 31, 160, 19), Qt.AlignLeft | Qt.AlignVCenter,
                         xp.text())
        painter.setPen(QColor('#E8F7FF'))
        painter.drawText(QRectF(88, 30, 160, 19), Qt.AlignLeft | Qt.AlignVCenter,
                         xp.text())

        # Barra real: 106x9, graduacao derivada do QProgressBar vivo.
        progress = 0.0
        if bar.maximum() > bar.minimum():
            progress = max(0.0, min(1.0, (bar.value() - bar.minimum()) /
                                     (bar.maximum() - bar.minimum())))
        painter.setPen(QPen(QColor(255, 188, 65, 225), 1))
        painter.setBrush(QColor(2, 19, 37, 230))
        painter.drawRoundedRect(QRectF(89.5, 52, 107, 10), 4.5, 4.5)
        fill_w = 103 * progress
        if fill_w > .25:
            fill = QLinearGradient(91, 54, 196, 54)
            fill.setColorAt(0, QColor('#078BFF'))
            fill.setColorAt(.5, QColor('#00D3F5'))
            fill.setColorAt(1, QColor('#75FFFF'))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(fill))
            painter.drawRoundedRect(QRectF(91, 54, fill_w, 6),
                                    min(3., fill_w / 2), 3.)
            painter.setBrush(QColor(207, 252, 255, 190))
            painter.drawEllipse(QPointF(91 + fill_w, 57), 1.5, 1.5)
        painter.end()

class _DashboardTrophyFloor(QFrame):
    """Suporte invisivel e clicavel para o trofeu na cena do Dashboard.

    O halo e desenhado aqui, nunca no GIF e nunca no fundo de outros cards.
    """

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        center = self.width() * 0.40
        for width, alpha in ((126, 44), (94, 76), (58, 98)):
            painter.setPen(QPen(QColor(255, 172, 28, alpha), 1.25))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QRectF(center - width / 2, self.height() - 13,
                                      width, 9))
        painter.end()


class _DashboardFloatingProgress(QObject):
    """Divide apenas a exibicao do Progresso em dois HUDs sobre o canvas.

    Reutiliza os componentes e os sinais originais; por isso as atualizacoes
    vindas do snapshot de gamificacao em main.py nao precisam ser tocadas.
    O parent eh dashboardRoot, o mesmo canvas do GIF: nada e embutido na arte.
    """

    def __init__(self, header):
        super().__init__(header)
        self.header = header
        self.root = None
        self.xp_panel = None
        self.trophy_panel = None
        self.futurista = False
        self.installed = False
        self.scheduled = False
        self.recommendation = None
        header.installEventFilter(self)
        self._schedule()

    def eventFilter(self, watched, event):
        t = event.type()
        if watched is self.header and t in (QEvent.Type.Show, QEvent.Type.ParentChange):
            self._schedule()
        if watched is self.root and t in (QEvent.Type.Resize, QEvent.Type.Show):
            self._schedule()
        if watched is self.recommendation and t in (
                QEvent.Type.Move, QEvent.Type.Resize, QEvent.Type.Show):
            self._schedule()
        return super().eventFilter(watched, event)

    def _schedule(self):
        if self.scheduled:
            return
        self.scheduled = True
        QTimer.singleShot(0, self._sync)

    def set_theme(self, theme):
        self.futurista = (theme == 'futurista')
        self._schedule()

    def _find_root(self):
        parent = self.header.parentWidget()
        while parent is not None:
            if parent.objectName() == 'dashboardRoot':
                return parent
            parent = parent.parentWidget()
        return None

    def _sync(self):
        self.scheduled = False
        root = self._find_root()
        if root is None:
            return  # Cabecalho ainda nao foi inserido no Dashboard.
        if self.root is not root:
            if self.root is not None:
                self.root.removeEventFilter(self)
            self.root = root
            root.installEventFilter(self)
        # Acompanhar o card verdadeiro; nao usar Y fixo dependente da janela.
        recommendation = root.findChild(QFrame, 'dashboardTodayAction')
        if recommendation is not self.recommendation:
            if self.recommendation is not None:
                self.recommendation.removeEventFilter(self)
            self.recommendation = recommendation
            if recommendation is not None:
                recommendation.installEventFilter(self)
        if self.futurista and not self.installed:
            self._detach_from_header()
        elif not self.futurista and self.installed:
            self._restore_to_header()
        if self.installed:
            self._place()

    def _detach_from_header(self):
        header = self.header
        old = header.progresso_resumo
        xp_panel = _DashboardAuraHorizontal(self.root)
        xp_panel.setObjectName('dashboardFloatingXP')
        xp_panel.setFixedSize(270, 80)
        xp_panel.setStyleSheet(
            'QFrame#dashboardFloatingXP {background: transparent; border: none;}')
        # Reutilizar integralmente os controles atualizados pelo motor.
        # Eles nao sao exibidos em duplicidade: QPainter representa a
        # mesma informacao num unico HUD, e os widgets seguem vivos.
        badge = header.progresso_badge
        level = header.progresso_nivel
        xp = header.progresso_xp
        progress = header.progresso_barra
        for model in (badge, level, xp, progress):
            model.setParent(xp_panel)
            model.hide()
        progress.setFixedSize(106, 9)
        xp_panel.bind_sources(badge, level, xp, progress)

        trophy_panel = _DashboardTrophyFloor(self.root)
        trophy_panel.setObjectName('dashboardFloatingAchievements')
        trophy_panel.setFixedSize(198, 81)
        trophy_panel.setStyleSheet('''
            QFrame#dashboardFloatingAchievements { background: transparent; border: none; }
            QPushButton#dashboardTopAchievements {
                background: transparent; border: none; color: #FFFFFF;
                font-size: 13px; font-weight: 700; text-align: left;
                padding: 0px; border-radius: 7px;
            }
            QPushButton#dashboardTopAchievements:hover,
            QPushButton#dashboardTopAchievements:focus {
                background: rgba(0, 50, 66, 90); border: 1px solid #00BEE7;
            }
        ''')
        lay = QHBoxLayout(trophy_panel)
        lay.setContentsMargins(4, 1, 4, 9)
        button = header.progresso_conquistas
        button.setParent(trophy_panel)
        button.setFixedSize(186, 64)
        button.setIconSize(QSize(40, 40))
        lay.addWidget(button)
        # O QFrame de 390x55 deixa de ocupar a primeira linha.
        # Mantemos seu objeto existente para compatibilidade com outros temas.
        old.hide()
        self.xp_panel = xp_panel
        self.trophy_panel = trophy_panel
        self.installed = True
        header.progresso_hud_xp = xp_panel
        header.progresso_hud_conquistas = trophy_panel
        self._place()
        xp_panel.show()
        trophy_panel.show()
        xp_panel.raise_()
        trophy_panel.raise_()

    def _restore_to_header(self):
        header = self.header
        old = header.progresso_resumo
        old_row = old.layout()
        badge = header.progresso_badge
        level = header.progresso_nivel
        xp = header.progresso_xp
        bar = header.progresso_barra
        trophy = header.progresso_conquistas
        for w in (badge, level, xp, bar, trophy):
            w.setParent(old)
        old_row.insertWidget(0, badge, 0, Qt.AlignVCenter)
        nested = getattr(header, '_progresso_nivel_layout', None)
        if nested is not None:
            nested.addWidget(level)
            nested.addWidget(xp)
        bar.setFixedHeight(11)
        bar.setMinimumWidth(90)
        bar.setMaximumWidth(16777215)
        old_row.addWidget(bar, 1, Qt.AlignVCenter)
        trophy.setFixedSize(114, 44)
        trophy.setIconSize(QSize(31, 31))
        old_row.addWidget(trophy, 0, Qt.AlignVCenter)
        old.show()
        for w in (badge, level, xp, bar, trophy):
            w.show()
        self.xp_panel.hide()
        self.trophy_panel.hide()
        self.xp_panel.deleteLater()
        self.trophy_panel.deleteLater()
        self.xp_panel = None
        self.trophy_panel = None
        self.installed = False

    def _place(self):
        if not self.installed or self.root is None:
            return
        w, h = self.root.width(), self.root.height()
        # Em telas com rolagem, usar a altura visivel do canvas para que o
        # trofeu nao desapareca abaixo do viewport.
        view = self.root.parentWidget()
        if view is not None:
            h = min(h, view.height())
        if w <= 0 or h <= 0:
            return
        # Calibracao pela captura 1366x715: eixo X do Progresso ao lado do
        # cerebro, Y logo abaixo da faixa Planejamento; conquistas no piso.
        # Os clipes ficam dentro do canvas e acompanham o resize do Qt.
        # Ajuste fino O04-R5: deslocar o HUD completo 35 px a direita e
        # 16 px para cima em relacao a posicao anterior do Dashboard.
        # O desenho Aura 2.0, seus valores e o HUD de conquistas nao mudam.
        # Em janelas estreitas, limitar ao espaco visivel do Dashboard.
        xp_x_base = min(max(702, int(w * 0.57)), max(0, w - 275))
        xp_x = min(xp_x_base + 180, max(0, w - self.xp_panel.width() - 5))
        original_xp_y = max(92, int(h * 0.14))
        # Alinhar a BORDA INFERIOR do painel Nível/XP ao topo verdadeiro
        # da Recomendacao; a arte do GIF e os outros cards nao participam.
        xp_y = original_xp_y + 15  # reserva antes de concluir o layout Qt
        card = self.recommendation
        # Card real pode estar temporariamente em um painel do viewport.
        # Não reajustar o HUD ao deslocamento desse painel flutuante.
        if (card is not None and card.isVisible()
                and self.root.isAncestorOf(card)):
            top = card.mapTo(self.root, QPoint(0, 0)).y()
            if 0 < top < h:
                xp_y = top - self.xp_panel.height()
        xp_y = max(0, min(xp_y - 24, h - self.xp_panel.height()))
        tro_x = max(0, w - 240)
        # Conquistas preservadas na posição anterior, independente do XP.
        tro_y = max(original_xp_y + 100, min(int(h * 0.735), h - 98))
        self.xp_panel.move(xp_x, xp_y)
        self.trophy_panel.move(tro_x, tro_y)
        self.xp_panel.raise_()
        self.trophy_panel.raise_()

def criar_cabecalho_discreto_dashboard(abrir_busca, logo_pixmap=None, *,
                                      nivel_badge=None, abrir_conquistas=None) -> QFrame:
    """Conserva somente a logo no lugar da antiga faixa do Dashboard.

    Assinatura de parâmetros mantida para preservar o chamador existente.
    A pesquisa global permanece no Ctrl+K e na barra lateral.
    """
    painel = QFrame()
    painel.setObjectName("dashboardQuickNav")
    painel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    # Altura original preservada: cards e logo não mudam de posição.
    painel.setFixedHeight(72)
    # Mesma primeira linha de 72 px: a logo e a faixa de XP nao mudam.
    colunas = QVBoxLayout(painel)
    colunas.setContentsMargins(0, 0, 0, 0)
    # Espaco entre Progresso e Planejamento calibrado em aproximadamente
    # metade da distancia anterior (~23 px -> ~12 px), sem redimensionar
    # os cards nem seus elementos internos.
    colunas.setSpacing(3)
    linha = QHBoxLayout()
    linha.setContentsMargins(12, 5, 12, 5)
    linha.setSpacing(8)
    colunas.addLayout(linha)

    # A mesma assinatura T3 da Home, carregada do módulo oficial e sem
    # redesenho, recorte ou arquivo raster duplicado no pacote incremental.
    # Manter o fallback antigo caso o PNG oficial não possa ser decodificado.
    marca_oficial = QPixmap()
    try:
        oficial_ok = (marca_oficial.loadFromData(assinatura_cabecalho_png(), "PNG")
                      and not marca_oficial.isNull())
    except Exception:
        oficial_ok = False

    logo = QLabel()
    logo.setObjectName("dashboardQuickBrand")
    logo.setAlignment(Qt.AlignCenter)
    if oficial_ok:
        # Reproduz exatamente os limites e a escala utilizados na Home.
        logo.setFixedSize(215, 61)
        logo.setPixmap(marca_oficial.scaled(
            211, 58, Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        logo.setAccessibleName("VighnaStudy — marca oficial")
        logo.setToolTip("VighnaStudy — marca oficial")
    else:
        logo.setFixedSize(38, 43)
        if logo_pixmap is not None and not logo_pixmap.isNull():
            logo.setPixmap(logo_pixmap.scaled(
                38, 43, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
        logo.setToolTip("VighnaStudy")
    linha.addWidget(logo, 0, Qt.AlignVCenter)

    # Na assinatura oficial, o lettering já está dentro da própria arte.
    # Exibir o QLabel antigo duplicaria o nome e alteraria o layout.
    if not oficial_ok:
        nome = QLabel("VighnaStudy")
        nome.setObjectName("dashboardQuickBrandName")
        linha.addWidget(nome, 0, Qt.AlignVCenter)
    # Progresso horizontal: deslocado para o canto superior DIREITO, acima
    # da arte do cerebro. Mantem a instancia, dados, 390x55 e controles.
    # O stretch agora separa a logo do Progresso, preservando a faixa
    # Planejamento exclusivamente na segunda linha, alinhada a esquerda.
    linha.addStretch(1)
    resumo = QFrame(painel)
    resumo.setObjectName("dashboardTopProgressPanel")
    # Compactacao proporcional (~20%): 486x68 -> 390x55.
    # Mantem os valores reais de nivel, XP e conquistas e o clique original.
    resumo.setFixedSize(390, 55)
    resumo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    resumo_layout = QHBoxLayout(resumo)
    resumo_layout.setContentsMargins(8, 3, 8, 3)
    resumo_layout.setSpacing(6)

    if nivel_badge is None:
        nivel_badge = QLabel("1", resumo)
        nivel_badge.setAlignment(Qt.AlignCenter)
        nivel_badge.setStyleSheet(
            "color:white;font-size:14pt;font-weight:bold;"
            "border:3px solid #00D7F5;border-radius:22px;"
        )
    nivel_badge.setFixedSize(48, 48)
    nivel_badge.setProperty("dashboard_reference_ring", True)
    nivel_badge.setToolTip("Indicador de nivel; o preenchimento de XP usa os valores reais")
    resumo_layout.addWidget(nivel_badge, 0, Qt.AlignVCenter)
    # Preserva o inicio da tipografia mesmo com anel mais a esquerda.
    resumo_layout.addSpacing(2)

    nivel_xp = QVBoxLayout()
    nivel_xp.setContentsMargins(0, 0, 0, 0)
    nivel_xp.setSpacing(2)
    nivel = QLabel("Nível 1")
    nivel.setObjectName("dashboardTopProgressLevel")
    xp = QLabel("0 / 250 XP")
    xp.setObjectName("dashboardTopProgressXP")
    nivel.setMinimumWidth(76)
    nivel_xp.addWidget(nivel)
    nivel_xp.addWidget(xp)
    resumo_layout.addLayout(nivel_xp, 0)
    painel._progresso_nivel_layout = nivel_xp

    barra = QProgressBar(resumo)
    barra.setObjectName("dashboardTopProgressBar")
    barra.setRange(0, 100)
    barra.setValue(0)
    barra.setFixedHeight(11)
    barra.setTextVisible(False)
    barra.setMinimumWidth(90)
    barra.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    barra.setToolTip("Evolucao de XP para o proximo nivel")
    resumo_layout.addWidget(barra, 1, Qt.AlignVCenter)

    conquistas = QPushButton("0/0\nconquistas", resumo)
    conquistas.setObjectName("dashboardTopAchievements")
    conquistas.setFixedSize(114, 44)
    conquistas.setIcon(_icone_trofeu_referencia())
    conquistas.setIconSize(QSize(31, 31))
    conquistas.setCursor(Qt.PointingHandCursor)
    conquistas.setToolTip("Abrir Conquistas nas Estatísticas")
    conquistas.setAccessibleName("Ver conquistas")
    if abrir_conquistas is not None:
        conquistas.clicked.connect(abrir_conquistas)
    else:
        conquistas.setEnabled(False)
    resumo_layout.addWidget(conquistas, 0, Qt.AlignVCenter)
    linha.addWidget(resumo, 0, Qt.AlignVCenter)

    painel.progresso_resumo = resumo
    painel.progresso_badge = nivel_badge
    painel.progresso_nivel = nivel
    painel.progresso_xp = xp
    painel.progresso_barra = barra
    painel.progresso_conquistas = conquistas

    # Segunda linha: Planejamento modular, calibrado pelo card de referencia.
    # O controlador original em main.py continua preenchendo as MESMAS labels
    # com os valores reais de questoes, meta e revisoes pendentes.
    faixa = QFrame(painel)
    faixa.setObjectName("dashboardTopPlanningStrip")
    faixa.setFixedSize(655, 62)
    # Na referencia a faixa tem aproximadamente 810px e NAO ocupa toda a
    # largura do Dashboard. Em telas menores pode reduzir seu tamanho.
    # Largura exata corresponde ao alinhamento marcado; 655px.
    faixa.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
    fl = QHBoxLayout(faixa)
    fl.setContentsMargins(9, 5, 9, 5)
    fl.setSpacing(8)

    icone_dia = QLabel(faixa)
    icone_dia.setObjectName("dashboardTopPlanningIcon")
    icone_dia.setAlignment(Qt.AlignCenter)
    icone_dia.setFixedSize(46, 46)
    icone_dia.setPixmap(_icone_calendario_planejamento().scaled(
        37, 37, Qt.KeepAspectRatio, Qt.SmoothTransformation
    ))
    icone_dia.setAccessibleName("Planejamento de hoje")
    fl.addWidget(icone_dia, 0, Qt.AlignVCenter)

    bloco_data = QFrame(faixa)
    bloco_data.setObjectName("dashboardTopPlanningInfo")
    bloco_data.setFixedWidth(162)
    textos_dia = QVBoxLayout(bloco_data)
    textos_dia.setContentsMargins(0, 0, 0, 0)
    textos_dia.setSpacing(2)
    titulo_dia = QLabel("Planejamento de hoje", bloco_data)
    titulo_dia.setObjectName("dashboardTopPlanningTitle")
    titulo_dia.setToolTip("Planejamento de hoje")
    data_dia = QLabel("—", bloco_data)
    data_dia.setObjectName("dashboardTopPlanningDate")
    textos_dia.addWidget(titulo_dia)
    textos_dia.addWidget(data_dia)
    fl.addWidget(bloco_data, 0, Qt.AlignVCenter)

    divisor_1 = QFrame(faixa)
    divisor_1.setObjectName("dashboardTopPlanningSeparator")
    divisor_1.setFixedSize(1, 34)
    fl.addWidget(divisor_1, 0, Qt.AlignVCenter)

    # Contagem e barra formam UM modulo; percentual nao integra esta barra.
    bloco_questoes = QFrame(faixa)
    bloco_questoes.setObjectName("dashboardTopPlanningMetrics")
    bloco_questoes.setFixedWidth(153)
    metricas = QVBoxLayout(bloco_questoes)
    metricas.setSpacing(3)
    metricas.setContentsMargins(0, 0, 0, 0)
    questoes = QLabel("—", bloco_questoes)
    questoes.setObjectName("dashboardTopPlanningQuestions")
    questoes.setToolTip("Questões realizadas e meta diária")
    barra_dia = QProgressBar(bloco_questoes)
    barra_dia.setObjectName("dashboardTopPlanningBar")
    barra_dia.setRange(0, 100)
    barra_dia.setValue(0)
    barra_dia.setTextVisible(False)
    barra_dia.setFixedHeight(9)
    metricas.addWidget(questoes)
    metricas.addWidget(barra_dia)
    fl.addWidget(bloco_questoes, 0, Qt.AlignVCenter)

    percentual = QLabel("—", faixa)
    percentual.setObjectName("dashboardTopPlanningPercent")
    percentual.setToolTip("Percentual de questões concluídas no dia")
    percentual.setAlignment(Qt.AlignCenter)
    percentual.setFixedWidth(103)
    fl.addWidget(percentual, 0, Qt.AlignVCenter)

    divisor_2 = QFrame(faixa)
    divisor_2.setObjectName("dashboardTopPlanningSeparator")
    divisor_2.setFixedSize(1, 34)
    fl.addWidget(divisor_2, 0, Qt.AlignVCenter)

    revisoes_icon = QLabel(faixa)
    revisoes_icon.setObjectName("dashboardTopPlanningReviewIcon")
    revisoes_icon.setAlignment(Qt.AlignCenter)
    revisoes_icon.setFixedSize(26, 26)
    revisoes_icon.setPixmap(_icone_revisoes_planejamento().scaled(
        24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation
    ))
    fl.addWidget(revisoes_icon, 0, Qt.AlignVCenter)

    revisoes = QLabel("0 revisões", faixa)
    revisoes.setObjectName("dashboardTopPlanningRevisions")
    revisoes.setToolTip("Revisões pendentes")
    revisoes.setFixedWidth(76)
    revisoes.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    fl.addWidget(revisoes, 0, Qt.AlignVCenter)

    # O card compacto de Planejamento foi removido visualmente do Dashboard.
    # Preservar os controles (ocultos) para os atualizadores de dados do
    # main.py, sem criar novos calculos nem afetar a pagina Meu Edital.
    # A faixa NAO participa mais do layout e nao pode aparecer no canvas.
    faixa.hide()
    faixa.setFixedSize(0, 0)
    # Preservar a linha de 655 x 62 sem pintar qualquer superficie.
    # Um QWidget vazio recebe estilos globais (fundo azul-escuro), criando
    # a faixa fantasma vista apos a remocao. QSpacerItem NAO e widget:
    # nao pinta fundo/borda, nao intercepta cliques e nao muda a geometria.
    reserva = QSpacerItem(655, 62, QSizePolicy.Fixed, QSizePolicy.Fixed)
    colunas.addItem(reserva)
    painel.planejamento_faixa = faixa
    painel.planejamento_data = data_dia
    painel.planejamento_questoes = questoes
    painel.planejamento_percentual = percentual
    painel.planejamento_barra = barra_dia
    painel.planejamento_revisoes = revisoes

    # O campo de busca do Dashboard foi removido. O controlador global não
    # é alterado, e a lupa lateral inserida no lote anterior continua ativa.
    painel.busca_global = None
    painel.marca = logo
    painel._floating_progress = _DashboardFloatingProgress(painel)
    return painel


def aplicar_estilo_cabecalho_dashboard(painel: QFrame, tema: str) -> None:
    """Usa tokens do Design System sem modificar cores globais."""
    painel.setStyleSheet((render_native_qss(QSS_CABECALHO_DASHBOARD) if tema == "futurista"
                        else render_qss(tema, QSS_CABECALHO_DASHBOARD)))
    # Temas legados mantem o progresso no card original, sem duplicacao.
    if hasattr(painel, "_floating_progress"):
        painel._floating_progress.set_theme(tema)
    elif hasattr(painel, "progresso_resumo"):
        painel.progresso_resumo.setVisible(tema == "futurista")
