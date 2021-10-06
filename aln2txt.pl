#!/usr/bin/perl

use strict;
use warnings;


my $qlstfn = shift || die;
my $tlstfn = shift || die;
my $alnfn = shift || die;


my %qlst = ();
my %qlen = ();
my $count = 0;
open(INPUT, $qlstfn);
foreach (<INPUT>) {
  chomp;
  my ($seqid, $seqlen) = split(/\s+/);

  $qlst{$seqid} = $count;
  $count += 1;
  $qlen{$seqid} = $seqlen;
}
close(INPUT);

my %tlst = ();
my %tlen = ();
$count = 0;
open(INPUT, $tlstfn);
foreach (<INPUT>) {
  chomp;
  my ($seqid, $seqlen) = split(/\s+/);

  $tlst{$seqid} = $count;
  $count += 1;
  $tlen{$seqid} = $seqlen;
}
close(INPUT);

my %hist = ();
print join("\t", "#shape:", 1, scalar keys %tlst, 9), "\n";
open(INPUT, $alnfn);
foreach (<INPUT>) {
  chomp;
  my ($qid, $tid, $seqid, $alnlen, $nmiss, $ngap, $qbegin, $qend, $tbegin, $tend, $evalue, $bscore) = split(/\t/);
  $qid =~ s/[,\|].*$//;
  $tid =~ s/[,\|].*$//;
  $seqid /= 100.0 if $seqid > 1.0;
  $nmiss = sprintf("%.3f", 1.0 - $nmiss / $alnlen);
  $ngap = sprintf("%.3f", 1.0 - $ngap / $alnlen);
  my $qcov = sprintf("%.3f", ($qend - $qbegin + 1) / $qlen{$qid});
  my $tcov = sprintf("%.3f", ($tend - $tbegin + 1) / $tlen{$tid});

  next if defined $hist{"$qid:$tid"};
  $hist{"$qid:$tid"} = 1;
  $bscore = sprintf("%.3f", $bscore / $alnlen);
  next unless $bscore > 0.5;  # note

  print join("\t", $tid, $tlst{$tid}, $seqid, $nmiss, $ngap, $qcov, $tcov, $bscore, $qlen{$qid}, $tlen{$tid}, $alnlen), "\n";
}
close(INPUT);

