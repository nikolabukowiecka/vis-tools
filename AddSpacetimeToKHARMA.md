Proceed to "../kharma/kharma/coordinates/coordinate_systems.hpp" and define a new class for your metric.
Note: for a chosen coordinate system you need to implement a Jacobian to convert to the Boyer Lindquist cooridnates, so KHARMA can ultimately convert to the native coordinates (Cartesian coordinates, since HARM is logically Cartesian).
Create constructions and function holders, and set the tranformation to the native coordiantes in "../kharma/kharma/coordinates/coordinate_emmbedding.hpp".
(Use KHinKS - KerrHayward implemented in ingoing Kerr Schild coordinates)