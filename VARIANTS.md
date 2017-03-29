# PL0-Language-Tools

This is a fork of tangentstorm's repo at https://github.com/tangentstorm/PL0-Language-Tools.git
which is itself a fork of https://github.com/oriontransfer/PL0-Language-Tools.git

# Targets

## Retro

Developed by tangentstorm, this served as my initial model for the other targets.

## Parable

Parable is an experimental stack based language I'm developing. See http://forthworks.com/parable
for details on it.

Variable scope remains an issue at this time.

For instance:

    var x;
    procedure a;
      var x;
      begin
        x := 2;
        ! x
      end;
    begin
      x := 10;
      call a;
      ! x
    end.

Compiles to:

    'x' variable
    [ ] 'a' define
    'x' variable
    [  #2 &x !  &x @ slice.store/advance ] 'a' define
    [  #10 &x ! a &x @ slice.store/advance ] 'run' define

It should compile to:

    'a:x' variable
    [ ] 'a' define
    [  #2 &a:x !  &a:x @ slice.store/advance ] 'a' define

    'x' variable
    [  #10 &x ! a &x @ slice.store/advance ] 'run' define


## ANS FORTH

Mostly a trivial adaption of the Retro target.
