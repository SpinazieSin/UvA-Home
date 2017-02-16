module syntaxtest

import String;
import IO;

layout Whitespace = [\t\n\r\f\ ]*;

lexical N = "giraffe" | "elephant";
lexical Place = "Amsterdam"; // list of places from file here
// maybe shorten into "Pre"
lexical Preposition = "around" | "near" | "at" | "in" | "within" | "from"; 
lexical Det = "the" | "a";

syntax NP
 = N n 
 | Det d N n
 ;
 
syntax Region
 = Place place // Give me news about Amsterdam (I believe "about" is not a preposition)
 | Preposition pre Place place
 ;

public void main(list[str] args) {
    // cwd = current working dir
    loc file = |cwd:///Places/cities.txt|;
    list[str] cities = readPlaces(file);
}

public list[str] readPlaces(loc file) { 
    return split("\n", readFile(file));
}
