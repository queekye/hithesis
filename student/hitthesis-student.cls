%% Non-official derived wrapper for hithesisbook, not an upstream class.
%% Copyright (C) 2017--2026 hithesis contributors (upstream code).
%% Copyright (C) 2026 queekye (this separately named student extension).
%% Based on hithesis/hithesis master 04963b5; upstream files remain unchanged.
%% Distributed under LPPL 1.3a or later; upstream CC BY-NC 4.0 notice retained.
%% See LICENSE and FORK-NOTES.md for source, maintenance and attribution.
\NeedsTeXFormat{LaTeX2e}[2021/06/01]
\ProvidesClass{hitthesis-student}[2026/10/09 v0.1 Non-official HIT student wrapper]
\RequirePackage{kvoptions}
\SetupKeyvalOptions{family=hitstudent,prefix=hitstudent@,setkeys=\kvsetkeys}
\DeclareBoolOption[false]{guide2025}
\DeclareStringOption[legacy]{degreecategory}
\DeclareBoolOption[false]{anonymous}
\DeclareBoolOption[false]{tocfix}
\DeclareBoolOption[false]{floatlayout}
\DeclareBoolOption[true]{fixhidden}
\DeclareStringOption[upstream]{layout}
\DeclareDefaultOption{\PassOptionsToClass{\CurrentOption}{hithesisbook}}
\ProcessKeyvalOptions*
\LoadClass{hithesisbook}
\RequirePackage{hitstudent-core}
\ClassInfo{hitthesis-student}{Non-official student wrapper maintained by queekye;
  upstream hithesisbook is loaded without source replacement}
\endinput
