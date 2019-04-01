%SO2 Representation of 2D rotation
%
% This subclasss of RTBPose is an object that represents an SO(2) rotation
%
%         SpatialVec6 (abstract handle class)
%            |
%            +--- SpatialM6 (abstract)
%            |     |
%            |     +---SpatialVelocity
%            |     +---SpatialAcceleration
%            |
%            +---SpatialF6 (abstract)
%                  |
%                  +---SpatialForce
%                  +---SpatialMomentum
%
% SO2.A is an SO2 object representing null rotation.
%
% SO2.A() is an SO2 object representing null rotation.
%
% P = SO2() is an SO2 object representing null rotation.
%
% P = SO2.A() is an SO2 object representing null rotation.
%
% P = SO2(C,D) is an SO2 object representing null rotation.
%
% [X,Y] = SO2(C,D) is an SO2 object representing null rotation.
%
% P = SO2(...) is an SO2 object representing null rotation.
%
% X = A * B is an SO2 object representing null rotation.
%
% X = A ^ B is an SO2 object representing null rotation.
%
% X = A ./ B is an SO2 object representing null rotation.
%
% Simple para for i^th and X in R^N or P^N or X^N.
%
% Simple para V(1xN), V(N+1xN-1), V(2x3x4), V(N+1xN+1xN-1).
%
% Constructor methods::
%  SO2          general constructor
%  SO2.exp      exponentiate an so(2) matrix
%  SO2.rand     random orientation
%  new          new SO2 object
%
% Information and test methods::
%  dim*         ^returns 2
%  isSE*        ^returns false
%  issym*       ^^true if rotation matrix has symbolic elements
%  isa          ^^^check if matrix is SO2 and has
%               a continuation line
%
%
% ^ means inherited from RTBPose
%
% Operators::
%  +           elementwise addition, result is a matrix
%  -           elementwise subtraction, result is a matrix
%  *           multiplication within group, also group x vector
%  /           multiply by inverse
% .*           multiple and normalize
% ^            exponentiate
%  ==          test equality
%  ~=          test inequality
%
% Options::
%  'deg'   Compute angles in degrees (default radians)
%  'xyz'   Return solution for sequential rotations about X, Y, Z axes
%  'yxz'   Return solution for sequential rotations about Y, X, Z axes
%
% Notes::
% - ^ is inherited from RTBPose.
% - ^^ is inherited from RTBPose.
% - ^^^ is inherited from RTBPose.
% - If either, or both, of P1 or P2 are vectors, then the result is a vector.
%  - if P1 is a vector (1xN) then R is a vector (1xN) such that R(i) = P1(i).*P2.
%  - if P2 is a vector (1xN) then R is a vector (1xN) such that R(i) = P1.*P2(i).
%  - if both P1 and P2 are vectors (1xN) then R is a vector (1xN) such 
%    that R(i) = P1(i).*P2(i).
%
%
% See also SE2, SO3, SE3, RTBPose.
