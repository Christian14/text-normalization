#!/usr/bin/perl

################################################################
# Autor: Xavier López Morrás (2005)
#
# prolepsi@yahoo.es
# 
# separador.pl   SEPARADOR DE SÍLABAS Y ACENTUADOR . 
# INPUT: transcripcion.
# OUTPUT: transcripcion silabificada y acentuada.
################################################################


#####################################################################
####    Puedes hacer uso libre del script y código a nivel personal.
####    Para otras finalidades consultar al autor.
#####################################################################

print proc_sil("awtomatiko");
print "\n";

sub proc_sil {


#recogemos el argumento que es la transcripcion fonetica sin separacion de silabas ni acentos
local $transcripcion= shift;

#convertiendo carácteres para procesar con más facilidad
$transcripcion =~ s/&gamma;/G/g;
$transcripcion =~ s/&theta;/Z/g;
$transcripcion =~ s/&beta;/B/g;
$transcripcion =~ s/&#345;/R/g;
$transcripcion =~ s/t&int;/X/g;
$transcripcion =~ s/ð/D/g;
$transcripcion =~ s/&lambda;/L/g;
$transcripcion =~ s/&#331;/ç/g;
$transcripcion =~ s/^ +//g;

#creamos un array cuyos elementos son las palabras 
@palabras= split(/ /,$transcripcion);
local $n=0;



##########################################################################################
## procesamiento de una palabra
##########################################################################################

for (@palabras) {
local $palabra=$palabras[$n];
local $n2=-1;

        ###################################################################################
        ##    procesamiento de una silaba individual
        ###################################################################################
        #for ($n3=0; (length($palabra)) >= $n3; $n3++) {
        while ( (substr($palabra,$n2,1)=~/./) ) {
        $letra0= substr($palabra,$n2,1);
        $letra1= substr($palabra,$n2-1,1);
        $letra2= substr($palabra,$n2-2,1);
        $letra3 =substr($palabra,$n2-3,1);
        $letra4 =substr($palabra,$n2-4,1);
        $letra_sig=substr($palabra,$n2+1,1);
        local $silaba="8xz";
        #print "<font color=grey>-$letra0-</font>";

                #caso CV
                if ($letra0=~/[aeiouAEIOU]/) {
                        if ($letra1=~/[bBcdDfgGhklLmnNñprRstvxXyzZ]/) {
                        unless ( ($letra2=~/[tkpgGdDfbB]/) && ($letra1=~/[rl]/)   ) {
                        $silaba=$letra1.$letra0;
                        ##print "$silaba!!<br>";
                        $n2--;

                        }
                        }
                }

                #caso CVC
                if ($letra0=~/[nszrNpkmMlLZçdDgb]/) {
                        if ($letra1=~/[aeiouAEIOU]/) {
                                if ($letra2=~/[bBcdDfgGhklLmnNñprRstvxXyzZ]/) {
                                unless( ($letra3=~/[tkpgGdDfbB]/) && ($letra2=~/[rl]/)  ) {
                                $silaba="$letra2"."$letra1"."$letra0";
                                ##print "$silaba*<br>";
                                $n2=$n2-2;}
                                }
                        }
                }

                #caso V
                if ( ($letra0=~/[aeiouAEIOU]/) )  {
                unless ( ($letra1=~/[bBcdDfgGhklLmnNñprRstvxXyzZ]/) || ($letra1=~/[jw]/) ) {
                $silaba= "$letra0";
                ##print "$silaba?<br>";
                }
                }

                #caso VC
                if ( ($letra0=~/[nszrNpkmMlLZçdDgb]/) && ($letra1=~/[aeiouAEIOUwj]/) ) {
                unless ($letra2=~/[bBcdDfgGhklLmnNñprRstvxXyzZ]/ || ($letra2=~/[jw]/) ) {
                $silaba= $letra1.$letra0;
                ##print "$silaba-<br>";
                $n2--;
                }
                }


                #caso VCC
                if ( ($letra0=~/[s]/) && ($letra1=~/[kn]/) && ($letra2=~/[aeiouAEIOU]/) ) {
                $silaba= $letra2.$letra1.$letra0;
                $n2=$n2-2;
                ##print "$silaba*<br>";
                }

                #caso CCV

                if ( ($letra0=~/[aeiouAEIOU]/) && ($letra1=~/[rl]/) && ($letra2=~/[tkpgGdDfbB]/) )
                {$silaba= $letra2.$letra1.$letra0;
                ##print "$silaba<br>";
                $n2=$n2-2;}

                #caso CCVC
                if ( ($letra0=~/[nszrNpkmMlLZçdDgb]/) && ($letra1=~/[aeiouAEIOU]/) && ($letra2=~/[rl]/) && ($letra3=~/[tkpgGdDfbB]/))                {$silaba= $letra3.$letra2.$letra1.$letra0;
                ##print "$silaba<br>";
                $n2=$n2-3;}

                #caso CVCC
                if ( ($letra0=~/[s]/) && ($letra1=~/[b]/) && ($letra2=~/[aeiouAEIOU]/) && ($letra3=~/[s]/) )
                {$silaba= $letra3.$letra2.$letra1.$letra0;
                $n2=$n2-3;}


                #diptongos
                #caso CVv y Vv
                if ( ($letra0=~/[jw]/) && ($letra1=~/[aeiou]/) ) {
                        if ($letra2 =~/[bBcdDfgGhklLmnNñprRstvxXyzZ]/) {
                        $silaba= $letra2.$letra1.$letra0;
                        ##print "$silaba<br>";

                        $n2=$n2-2;
                        }

                        elsif ( ($letra0=~/[jw]/) && ($letra1=~/[aeiou]/) ) {
                        $silaba= $letra1.$letra0;
                        ##print "$silaba¿¿<br>";

                        $n2--;
                        }
                }

                #caso CvV
                if ( ($letra0=~/[aeiouAEIOU]/) && ($letra1=~/[jw]/) ) {
                        if (($letra2 =~/[bBcdDfgGhklLmnNñprRstvxXyzZ]/) ) {
                        unless ($encontrada==1) {
                        $silaba = $letra2.$letra1.$letra0;
                        ##print "$silaba-<br>";

                        $n2=$n2-2;
                        }
                        }

                        elsif ( ($letra0=~/[aeiou]/) && ($letra1=~/[jw]/) ) {
                        $silaba= $letra1.$letra0;
                        ##print "$silaba<br>";

                        $n2--;
                        }
                }

                #caso CvVC
                if ( ($letra0=~/[cksznNplrçm]/) && ($letra1=~/[aeiouAEIOU]/) && ($letra2=~/[wj]/)
                && ($letra3=~/[bBcdDfgGhklLmnNñprRstvxXyzZ]/) ) {
                $silaba= $letra3.$letra2.$letra1.$letra0;
                ##print "$silaba<br>";
                $n2 = $n2-3;
                }


                #caso CCvV
                if ( ($letra0=~/[aeiou]/) && ($letra1=~/[jw]/) && ($letra2=~/[rl]/) && ($letra3=~/[tkpgGdDfbB]/) ) {
                $silaba= $letra3.$letra2.$letra1.$letra0;
                $n2= $n2-3;
                }

                #caso CCVv
                if ( ($letra0=~/[jw]/) && ($letra1=~/[aeiou]/) && ($letra2=~/[rl]/) && ($letra3=~/[tkpgGdDfbB]/) ) {
                $silaba= $letra3.$letra2.$letra1.$letra0;
                $n2= $n2-3;
                }

                #caso CCvVC
                if ( ($letra0=~/[cksznNplrçm]/) && ($letra1=~/[aeiou]/) && ($letra2=~/[jw]/) && ($letra3=~/[rl]/) &&
                ($letra4=~/[tkpgGdDfbB]/) ) {
                $silaba= $letra4.$letra3.$letra2.$letra1.$letra0;
                $n2= $n2-4;
                }


                ################################## fin diptongos ############################

                #caso CCVCC
                if ( ($letra0=~/s/) && ($letra1=~/[n]/) && ($letra2=~/[aeiouAEIOU]/) && ($letra3=~/[r]/)
                && ($letra4=~/[tkpgGdDfbB]/) ) {
                $silaba= $letra4.$letra3.$letra2.$letra1.$letra0;
                ##print "$silaba*<br>";
                $n2= $n2-4;
                }


                #otros casos
                if ( ($letra0=~/[jw]/) )  {
                unless ( $letra1=~/[aeioubBcdDfgGhklLmnNñprRstvxXyzZ]/  ) {
                $silaba= $letra0;
                ##print "$silaba*<br>";
                ##$tonica_encontrada=1;
                }
                        if ($letra1=~/[bBcdDfgGhklLmnNñprRstvxXyzZ]/) {
                        $silaba=$letra1.$letra0;
                        print "$silaba:<br>";
                        $n2--;
                        }
                }



                if ($silaba=="8xz") {
                $silaba="?";
                }


                #comprobamos si es tónica con acento


                unshift(@word,$silaba);

                $n2--;
                }




                #############################################################################################
                ############################## fin procesamiento silaba  ###################################            

####asignamos el acento si hay tónica
local $n5=0;

for (@word) {
if ($word[$n5]=~/[AEIOU]/) {
$word[$n5]= "'".$word[$n5];
$tonica_encontrada=1;
}
$n5++;
}



####### acentos por defecto #######################

unless (($tonica_encontrada==1)) {
if (@word>1) {                                  # si no es monosilabo....

if ($word[-1]=~/[rlZdD]$/) {                    # si la ultima silaba acaba en C 
$word[-1]="'"."$word[-1]";
}


else {
$word[-2]="'"."$word[-2]";
}
}


if ((@word==1) && ($word[0]=~/ir|ba|Ba/)) {
$word[0]="'"."$word[0]";
}

elsif ( (@word==1) && ($word[0]=~/[^']..+/)) {    #si es monosilabo y tiene 3 o mas letras
unless ($word[0]=~/^lo[sz]$|^la[sz]$/) {                #excepto 'los' y 'las'  
$word[0]="'"."$word[0]";
}}
}

#añadimos la palabra a la frase en formas de elementos (=silabas)  de un array 
push(@phrase_sil, @word);
#reseteamos la palabra
@word=();
$tonica_encontrada=0;

$n++;
}
############ convertimos de nuevo los caracteres para ser visualizador en pagina web ######################
local $n4=0;
for (@phrase_sil) {
$phrase_sil[$n4] =~ s/G/&gamma;/g;
$phrase_sil[$n4] =~ s/Z/&theta;/g;
$phrase_sil[$n4] =~ s/B/&beta;/g;
$phrase_sil[$n4] =~ s/R/&#345;/g;
$phrase_sil[$n4] =~ s/X/t&int;/g;
$phrase_sil[$n4] =~ s/D/ð/g;
$phrase_sil[$n4] =~ s/ç/&#331;/g;
$phrase_sil[$n4] =~ tr/AEIOU/aeiou/;
$phrase_sil[$n4] =~ s/L/&lambda;/g;
$n4++;
}






############################################################################################################
############################ fin procesamiento palabra ####################################################
return @phrase_sil;
}
############################### fin separador de silabas ##################################################
1;


