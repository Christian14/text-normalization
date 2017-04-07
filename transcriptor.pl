#!/usr/bin/perl

##################################################################
####    AUTOR: Xavier López Morrás
####    
####    SCRIPT: Transcriptor fonético automático del español
####    EMAIL:  prolepsi@yahoo.es
##################################################################
## INPUT: escritura ordinaria. OUTPUT: transcripcion fonetica.

sub caracteres  {

local $Frasev= shift;
$Frasev =~ tr/+/ /;
$Frasev =~ s/%F1/ñ/g;
$Frasev =~ s/%E1/á/g;
$Frasev =~ s/%E9/é/g;
$Frasev =~ s/%ED/í/g;
$Frasev =~ s/%F3/ó/g;
$Frasev =~ s/%FA/ú/g;
$Frasev =~ s/%2C/,/g;
$Frasev =~ s/%21/!/g;
$Frasev =~ s/%BF/¿/g;
$Frasev =~ s/%3F/?/g;
$Frasev =~ s/%FC/ü/g;
$Frasev =~ s/%DC/Ü/g;
$Frasev =~ s/%CD/Í/g;
$Frasev =~ s/%DA/Ú/g;
$Frasev =~ s/%C1/Á/g;
$Frasev =~ s/%C9/É/g;
$Frasev =~ s/%D3/Ó/g;
$Frasev =~ s/%3A/:/g;
$Frasev =~ s/%22/"/g;
substr ($Frasev, 0, 2) = "";
return $Frasev;
}


sub transcribe {

local $oracion=shift;

$oracion=~ s/%F1/ñ/g;
$oracion=~ s/%E1/á/g;
$oracion=~ s/%E9/é/g;
$oracion=~ s/%ED/í/g;
$oracion=~ s/%F3/ó/g;
$oracion=~ s/%FA/ú/g;
$oracion=~ s/%3A/|/g;
$oracion=~ s/%22//g;
$oracion=~ s/%FC/w/g;
$oracion=~ s/%DC/w/g;
$oracion=~ s/%CD/í/g;
$oracion=~ s/%DA/ú/g;
$oracion=~ s/%C1/á/g;
$oracion=~ s/%C9/é/g;
$oracion=~ s/%D3/ó/g;
$oracion=~ s/%2C/,/g;
$oracion=~ s/%21/,/g;
$oracion=~ s/%BF/,/g;
$oracion=~ s/%3F/,/g;
$oracion=~ tr/+/ /;
$oracion=~ tr/ABCDEFGHIJKLMNÑOPQ/abcdefghijklmnñopq/;
$oracion=~ tr/RSTUVWXYZ/rstuvwxyz/;

$medida = length ( $oracion ) ;
$esp=0;
$n = 0;
$voc = 0;
$rasgo= 0;


while ($n < $medida )
{

$c = substr ( $oracion, $n, 1 );
$vsig = substr ($oracion, $n+1, 1);
$vant = substr ($oracion, $n-1, 1);


if ($vsig eq " ") {
$esps = 1;
}
elsif ($vsig ne " ") {
$esps = 0;
}

$vsigg = substr ($oracion, $n+2, 1);
$impres="";


if ($vsigg eq " " || $vsig eq " " ) {
        $vsigg = substr ($oracion, $n+3, 1);
        }

if ($vsig eq " ") {
        $vsig = substr ($oracion, $n+2, 1); }


        if ($vsig eq "h" && $c ne "c") {
$vsig = $vsigg;
}


        if ($c eq "." || $c eq "," || $c eq ";") {
        $impres= "";
        $rasgo = 0; }

        if ($c eq " ") {
        $impres=" ";
        $esp = 1
        }

        if ($c eq "a")
        {
        $impres=  "a";
        $rasgo = "vocal";
        $voc = "a";
        $esp = 0;
        }

        if ($c eq "á")
        {
        $impres=  "A";
        $rasgo = "vocal";
        $voc = "a";
        $esp = 0;
        }

        if ($c eq "é") {
        $impres=  "E";
        $rasgo = "vocal";
        $voc = "e";
        $esp = 0; }


        if ($c eq "í")
        {
        $impres=  "I";
        $rasgo = "vocal";
        $voc = "ii";
        }

        if ($c eq "ó") {
        $impres=  "O";
        $rasgo = "vocal";
        $voc = "o";
        $esp = 0; }


        if ($c eq "ú")
        {
        $impres=  "U";
        $rasgo = "vocal";
        $voc = "uu";
        }


        #resto de letras
        if ($c eq "b")
        {

                if ($rasgo eq "vocal" || $rasgo eq "l" || $rasgo eq "r")
                {

                        if ($vsig=~/[aeiouáéíóúrl]/)    {
                        $impres="&beta;"; }

                        else
                        {
                        $impres=  "b";
                        }
                }
                else
                {
                $impres=  "b";
                }

        $rasgo = "b";
        }

        if ($c eq "c") {
                if ( $vsig eq "h" ) {
                $impres="t&int;";
                $n++;
                $rasgo = "tS"; }
                elsif ( $vsig eq "e" || $vsig eq "i" ||$vsig eq "í" ) {
                $impres="&theta;";
                $rasgo ="Z"; }
                else {
                $impres=  "k";
                $rasgo = "k"; }
                }

        if ($c eq "d") {
                if ($rasgo eq "vocal" || $rasgo eq "r")
                {
                        if ($vsig=~/[aeiouáéíóúrl]/)    {
                        $impres=  "ð" }

                        else {
                        $impres=  "d"; }
                }
                else
                {
                $impres=  "d";
                }
        $rasgo= "d";
        }

        if ($c eq "e") {
        $impres=  "e";
        $rasgo = "vocal";
        $voc = "e";
        $esp = 0; }


        if ($c eq "f") {
        $impres=  "f";
        $rasgo = f; }

        if ($c eq "g") {
                if ($vsig eq "a"|| $vsig eq "w")    {
                        if ($rasgo eq "vocal" || $rasgo eq "s" || $rasgo eq "r" || $rasgo eq "l") {
                        $impres=  "&gamma;";
                        }
                        else {
                        $impres=  "g"; }
                }
                elsif ($vsig eq "e") {
                        $impres=  "x"; }
                elsif ($vsig eq "i") {
                        $impres=  "x"; }
                elsif ($vsig eq "o") {
                        if ($rasgo eq "vocal" || $rasgo eq "s" || $rasgo eq "r" || $rasgo eq  "l") {
                        $impres=  "&gamma;"; }
                        else {
                        $impres=  "g" }
                }

                elsif ($vsig eq "u"|| $vsig eq "ú") {

                        if ( $vsigg eq "e" || $vsigg eq "i" ) {
                        $n++;
                                if ($rasgo eq "vocal" || $rasgo eq "s" || $rasgo eq "r" ||
                                $rasgo eq "l") {
                                $impres="&gamma;" }
                                else {
                                $impres=  "g"; }
                        }
                        else {
                                if ($rasgo eq "vocal"|| $rasgo eq "s" || $rasgo eq "r" ||
                                $rasgo eq "l") {
                                $impres="&gamma;" }
                                else {
                                $impres=  "g"; }
                }
                }
                elsif ($vsig eq "r"||$vsig eq "l") {
                          if ($rasgo eq "vocal"){
                          $impres="&gamma;";
                          $rasgo eq "G";}
                          else {
                          $impres=  "g";
                          $rasgo eq "g";}



                }

                else {
                        $impres=  "g"; }
                        $rasgo = "g";
        }


        if ($c eq "h") {
                }

        if ($c eq "i") {
                if ( ($rasgo eq "vocal") || ($vsig=~/[aeiouáéíó]/)  ) {
                unless ($vant=~/ /) {
                 $impres=  "j";
                 $rasgo = "vocal";
                 $voc = "ï";
                }
                }

                else {
                $impres=  "i";
                $rasgo = "vocal";
                $voc = "i";
                }
                if ($vant=~/ /) {
                $impres= "i";
                $esp = 0;
                }


        }

        if ($c eq "j") {
        $impres=  "x";
        $rasgo = x;
        }

        if ($c eq "k") {
        $impres=  "k";
        $rasgo = "k";
        }


        if ($c eq "l") {
                if ($vsig eq "l" && $vsigg ne "l" && $esps ne 1) {
                   if ($rasgo eq "vocal"){
                   $impres=  "&lambda;"}
                   elsif ($rasgo ne "vocal"){
                   $impres=  "&lambda;"}
                $n++;
                }

                elsif ($vsig eq "l" && $vsigg ne "l" && $esps eq 1) {
                $impres=  "l l";
                $n = $n+2;
                $esps = 0;
                }

                elsif ($vsig eq "l" && $vsigg eq "l" && $esps eq 1) {
                $impres=  "&lambda; &lambda;";
                $n = $n+3;
                $esps = 0;
                }

        else {
        $impres=  "l";
        $rasgo = "l";
        $esp = 0;
        }
        $rasgo = "l";

        }

        if ($c eq "m") {
                if ($vsig eq "f") {
                $impres=  "M"; }
                else {
                $impres=  "m";
                }
                $rasgo = "m";
        }

        if ($c eq "n") {
                if ($vsig eq "t" || $vsig eq "d" || $vsig eq "z")
                {
                $impres=  "N"; }

                elsif (($vsig eq "c" || $vsig eq "q") && ($vsigg eq "a" || $vsigg eq "o" || $vsigg eq "u")) {
                $impres="&#331;"; }

        elsif ($vsig eq "b"||$vsig eq "v"||$vsig eq "p" || $vsig eq "m"){
                $impres=  "m"; }

                elsif ($vsig eq "g" || $vsig eq "j"){
                $impres="&#331;";}

                elsif ($vsig eq "f"){
                $impres=  "M";}

                elsif (($vsig eq "c") && ($vsigg eq "e" || $vsigg eq "i")) {
                $impres=  "N"; }

                elsif ( (($vsig eq "y") && ($vsigg =~ /a|e|i|o|u/)) || ($vsig eq "l" && $vsigg eq "l") ) {
                $impres=  "ñ"; }
        else {
        $impres=  "n";
        }
                $rasgo = "n";

        }

        if ($c eq "ñ") {
        $impres=  "ñ";
        $rasgo ="ñ";
        }

        if ($c eq "o") {
        $impres=  "o";
        $rasgo = "vocal";
        $voc = "o";
        $esp = 0;}

        if ($c eq "p") {
        $impres=  "p";
        $rasgo = "p";
        }

        if ($c eq "q") {
        $impres=  "k";
        $n++;
        $rasgo = "q";
        }

        if ($c eq "r") {
                if ($rasgo eq "t" || $rasgo eq "d" || $rasgo eq "p" || $rasgo eq "b" || $rasgo eq "k" || $rasgo eq "g" ||$rasgo eq "f") {
        $impres="r";
        $rasgo = "r";
        }
                elsif ($vsig eq "r") {
                $rasgo = "r";}

                elsif ($vsig ne "r" && $rasgo eq "r" && $esp ne 1) {
                $impres="&#345;";
                $rasgo = "R";
                }
                elsif ($rasgo eq "vocal" && $vsig ne "r" && $esp ne 1) {
                $impres=  "r";
                $rasgo = "r";
                }
                elsif ($rasgo ne "vocal" && $esp eq 0) {
                $impres=  "&#345;";
                $rasgo = "r";
                }
                elsif ($esp eq 1 && $rasgo ne "R") {
                $impres=  "&#345;";
                $rasgo = "R";
                }
                elsif ($esp eq 1 && $rasgo eq "R") {
                $impres=  "r";
                $rasgo ="R";
                $esp= 0;}

                else{
                $impres=  "*";
                }
        }

        if ($c eq "s") {

                if ($vsig eq "b" || $vsig eq "v"|| $vsig eq "d"|| ($vsig eq "g" && ($vsigg ne "e" && $vsigg ne "i"))||$vsig eq "l"|| $vsig eq "m" || $vsig eq "n") {
                $impres=  "z";
                $rasgo = "vocal";}
        else {
        $impres=  "s";
        $rasgo = "s"; }
        }


        if ($c eq "t") {
        $impres=  "t";
        $rasgo = "t";
        }

        if ($c eq "u") {
           if ($rasgo eq "vocal" && $voc ne "ï")
           {
           $impres=  "w";
           $rasgo = "vocal";
           $voc = "w";
           }
           elsif ($vsig=~/[aeouáéó]/) {
           $impres=  "w";}

           else {
           $impres=  "u";
           $rasgo = "vocal";
           $voc = "u";}
           $esp = 0;
        }

        if ($c eq "v")
        {
                if ($rasgo eq "vocal" || $rasgo eq "l" || $rasgo eq "r")
                {


                        if ($vsig=~/[aeiouáéíóúrl]/)   {
                        $impres="&beta;";
                        $rasgo ="B";}

                        else
                        {
                        $impres=  "b";
                        }
                }
                else
                {
                $impres=  "b";
                }

        $rasgo = "b";

        }

        if ($c eq "w") {
        $impres=  "w";
        $rasgo = "w";
        }
        if ($c eq "x") {
        $impres=  "ks";
        $rasgo = "x" }



        if ($c eq "y") {
        if ($vsig =~/[aeiouáéíóú]/ && $esps eq 0) {
        $impres= "y";
        $rasgo= "vocal";
        $voc="ï";
        }

        elsif ($rasgo eq "vocal" || $esps eq 1) {
                  if (($rasgo eq "vocal"))
              {

                  $impres=  "i";  ##aproximante
                  $rasgo = "vocal";
                  $voc = "ï";

                  }
                  else {
                  $impres=  "i";
                  $rasgo = "vocal";
                  $voc = "i";
                  }
                  }


        else {
                $impres=  "y";
                }

        $esps = 0;

        }



        if ($c eq "z") {
        $impres="&theta;";
        $rasgo = "Z"; }

    if ($rasgo ne "vocal")
        {
        $voc = 0;
        }
$n++;

$transcripcion= $transcripcion.$impres;
}
return $transcripcion;
}
1;
