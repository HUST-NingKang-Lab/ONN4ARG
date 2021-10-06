#!/usr/bin/perl

use strict;
use warnings;
use autodie;


my ($seqid, $seqlen) = (undef, undef);
foreach (<>) {
  chomp;
  if (/^>/) {
    print "$seqid\t$seqlen\n" if defined $seqid;
    s/^>|[,\|].*$//g;
    $seqid = $_;
    $seqlen = 0;
  } else {
    s/\s+//g;
    $seqlen += length $_;
  }
}
print "$seqid\t$seqlen\n" if defined $seqid;

