------------------------- MODULE ReadThroughCache -------------------------
EXTENDS Naturals, TLC

CONSTANTS SkipFillFence, SkipJoinFence
Keys == {"a", "b"}
Readers == {"first", "second"}
None == "none"

VARIABLES db, payload, token, invalidated, failed, phase, key, seenToken,
          captured, joinedTo, last, blocked, independent
vars == <<db, payload, token, invalidated, failed, phase, key, seenToken,
          captured, joinedTo, last, blocked, independent>>

Init ==
  /\ db = [k \in Keys |-> "old"]
  /\ payload = [k \in Keys |-> None]
  /\ token = [k \in Keys |-> 1]
  /\ invalidated = {}
  /\ failed = {}
  /\ phase = [r \in Readers |-> "idle"]
  /\ key = [r \in Readers |-> "a"]
  /\ seenToken = [r \in Readers |-> 0]
  /\ captured = [r \in Readers |-> "old"]
  /\ joinedTo = [r \in Readers |-> None]
  /\ last = "none"
  /\ blocked = FALSE
  /\ independent = FALSE

\* A miss takes the token and a snapshot from the authoritative database.
Begin(r, k) ==
  /\ phase[r] = "idle"
  /\ payload[k] = None
  /\ phase' = [phase EXCEPT ![r] = "loading"]
  /\ key' = [key EXCEPT ![r] = k]
  /\ seenToken' = [seenToken EXCEPT ![r] = token[k]]
  /\ captured' = [captured EXCEPT ![r] = db[k]]
  /\ independent' = (independent \/
       (\E other \in Readers : other # r /\ phase[other] = "loading" /\
          key[other] = k /\ seenToken[other] # token[k]))
  /\ UNCHANGED <<db, payload, token, invalidated, failed, joinedTo,
                 last, blocked>>

\* A local waiter may reuse a pending load only under the same key and token.
Join(r, owner) ==
  /\ r # owner
  /\ phase[r] = "idle"
  /\ phase[owner] = "loading"
  /\ payload[key[owner]] = None
  /\ (SkipJoinFence \/ seenToken[owner] = token[key[owner]])
  /\ phase' = [phase EXCEPT ![r] = "joined"]
  /\ key' = [key EXCEPT ![r] = key[owner]]
  /\ seenToken' = [seenToken EXCEPT ![r] = token[key[owner]]]
  /\ joinedTo' = [joinedTo EXCEPT ![r] = owner]
  /\ captured' = [captured EXCEPT ![r] = captured[owner]]
  /\ last' = "join"
  /\ UNCHANGED <<db, payload, token, invalidated, failed, blocked,
                 independent>>

\* A successful delete atomically revokes the old identity and its payload.
Invalidate(k) ==
  /\ k \notin invalidated \cup failed
  /\ db' = [db EXCEPT ![k] = "new"]
  /\ payload' = [payload EXCEPT ![k] = None]
  /\ token' = [token EXCEPT ![k] = @ + 1]
  /\ invalidated' = invalidated \cup {k}
  /\ last' = "invalidate"
  /\ UNCHANGED <<failed, phase, key, seenToken, captured, joinedTo,
                 blocked, independent>>

\* Cache deletion may fail after the authoritative DB mutation commits.
FailedInvalidate(k) ==
  /\ k \notin invalidated \cup failed
  /\ db' = [db EXCEPT ![k] = "new"]
  /\ failed' = failed \cup {k}
  /\ last' = "failed-invalidation"
  /\ UNCHANGED <<payload, token, invalidated, phase, key, seenToken,
                 captured, joinedTo, blocked, independent>>

Complete(r) ==
  /\ phase[r] = "loading"
  /\ LET accepted == SkipFillFence \/ seenToken[r] = token[key[r]]
     IN /\ payload' = IF accepted
                          THEN [payload EXCEPT ![key[r]] = captured[r]]
                          ELSE payload
        /\ blocked' = (blocked \/ ~accepted)
        /\ last' = IF accepted THEN "filled" ELSE "blocked-fill"
  /\ phase' = [x \in Readers |->
       IF x = r \/ (phase[x] = "joined" /\ joinedTo[x] = r)
       THEN "done" ELSE phase[x]]
  /\ UNCHANGED <<db, token, invalidated, failed, key, seenToken,
                 captured, joinedTo, independent>>

Next ==
  (\E r \in Readers, k \in Keys : Begin(r, k)) \/
  (\E r, owner \in Readers : Join(r, owner)) \/
  (\E k \in Keys : Invalidate(k) \/ FailedInvalidate(k)) \/
  (\E r \in Readers : Complete(r))
Spec == Init /\ [][Next]_vars

TypeOK ==
  /\ \A k \in Keys : db[k] \in {"old", "new"} /\
       payload[k] \in {None, "old", "new"}
  /\ \A k \in Keys : token[k] \in {1, 2}
  /\ \A r \in Readers :
       phase[r] \in {"idle", "loading", "joined", "done"}
       /\ seenToken[r] \in {0, 1, 2}
       /\ captured[r] \in {"old", "new"}
NoStaleResurrection == \A k \in invalidated : payload[k] # "old"
SameTokenJoin == \A r \in Readers :
  phase[r] = "joined" => seenToken[r] = seenToken[joinedTo[r]]
FailedWriteCommits == \A k \in failed : db[k] = "new"
NoBlockedFillWitness == ~blocked
NoSameTokenJoinWitness == ~\E r \in Readers : phase[r] = "joined"
NoIndependentReadWitness == ~independent
NoFailedInvalidationWitness == failed = {}
=============================================================================
