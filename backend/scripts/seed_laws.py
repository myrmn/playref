"""Seed IFAB Laws and curated refereeing situations into Qdrant vector storage."""

import asyncio
import json
from pathlib import Path
import sys

# Ensure repo root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.app.config import settings
from backend.app.ingestion.models import LawChunk
from backend.app.ingestion.indexer import index_chunks, get_qdrant_client

LAW_TITLES = {
    1: "The Field of Play",
    2: "The Ball",
    3: "The Players",
    4: "The Players' Equipment",
    5: "The Referee",
    6: "The Other Match Officials",
    7: "The Duration of the Match",
    8: "The Start and Restart of Play",
    9: "The Ball in and out of Play",
    10: "Determining the Outcome of a Match",
    11: "Offside",
    12: "Fouls and Misconduct",
    13: "Free Kicks",
    14: "The Penalty Kick",
    15: "The Throw-in",
    16: "The Goal Kick",
    17: "The Corner Kick",
}

# Core statutory text snippets for all 17 Laws
CORE_LAW_TEXTS = {
    1: [
        ("1. Field surface & markings", 35, "Matches may be played on natural or artificial surfaces according to competition rules. The field of play must be rectangular and marked with continuous lines. The two longer boundary lines are touchlines. The two shorter lines are goal lines. All lines must be of the same width, which must be not more than 12 cm (5 ins)."),
        ("2. Goals and dimensions", 39, "A goal must be placed on the centre of each goal line. The distance between the inside of the posts is 7.32 m (8 yds) and the distance from the lower edge of the crossbar to the ground is 2.44 m (8 ft)."),
    ],
    2: [
        ("1. Qualities and measurements", 45, "The ball must be spherical, made of suitable material, of a circumference of between 68 cm (27 ins) and 70 cm (28 ins), and between 410 g (14 oz) and 450 g (16 oz) in weight at the start of the match."),
        ("2. Replacement of a defective ball", 46, "If the ball becomes defective during play, play is stopped and restarted with a dropped ball where the original ball became defective."),
    ],
    3: [
        ("1. Number of players", 49, "A match is played by two teams, each with a maximum of eleven players; one must be the goalkeeper. A match may not start or continue if either team has fewer than seven players."),
        ("2. Number of substitutions", 51, "Competition rules may allow a maximum of five substitutions per team. A player sent off before kick-off may be replaced by a named substitute without reducing the number of substitutions allowed."),
    ],
    4: [
        ("1. Safety and jewellery", 57, "A player must not use equipment or wear anything that is dangerous. All items of jewellery (necklaces, rings, bracelets, earrings, leather bands, rubber bands, etc.) are strictly forbidden and must be removed. Using tape to cover jewellery is not permitted."),
        ("2. Compulsory equipment", 58, "The compulsory equipment of a player comprises: a shirt with sleeves, shorts, socks, shinguards, and footwear. Shinguards must be made of suitable material to provide reasonable protection and be covered by the socks."),
    ],
    5: [
        ("1. The authority of the referee", 63, "Each match is controlled by a referee who has full authority to enforce the Laws of the Game. Decisions will be made to the best of the referee's ability according to the Laws of the Game and the 'spirit of the game'."),
        ("2. Decisions of the referee & restarts", 65, "The referee may not change a restart decision on realising that it is incorrect or on the advice of another match official if play has restarted or the referee has signalled the end of the first or second half."),
    ],
    6: [
        ("1. Assistant referees", 71, "Two assistant referees may be appointed whose duties are to indicate: when the whole ball has passed out of the field, which team is entitled to a corner kick, goal kick or throw-in, when a player in an offside position may be penalised, and when a substitution is requested."),
        ("2. Fourth official and VAR", 73, "The fourth official assists the referee at all times. A video assistant referee (VAR) may assist the referee only in the event of a 'clear and obvious error' or 'serious missed incident' relating to Goal/no goal, Penalty/no penalty, Direct red card, or Mistaken identity."),
    ],
    7: [
        ("1. Periods of play & half-time", 79, "A match lasts for two equal halves of 45 minutes, which may only be reduced if agreed between the referee and the two teams before the start of the match. Players are entitled to an interval at half-time, not exceeding 15 minutes."),
        ("2. Allowance for lost time", 80, "Allowance is made by the referee in each half for all playing time lost through: substitutions, assessment/removal of injured players, wasting time, disciplinary sanctions, and VAR checks and reviews."),
    ],
    8: [
        ("1. Kick-off procedure", 83, "A kick-off starts both halves of a match, both halves of extra time and restarts play after a goal has been scored. The ball is in play when it is kicked and clearly moves in any direction. A goal may be scored directly against the opponents from the kick-off; if the ball directly enters the kicker's goal, a corner kick is awarded to the opponents."),
        ("2. Dropped ball", 85, "The referee drops the ball for one player of the team that last touched the ball at the position where it last touched a player. If play was stopped when the ball was in the penalty area, the ball is dropped for the defending team goalkeeper."),
    ],
    9: [
        ("1. Ball out of play", 89, "The ball is out of play when it has wholly passed over the goal line or touchline on the ground or in the air, or play has been stopped by the referee."),
        ("2. Ball in play", 90, "The ball is in play at all other times, including when it rebounds off a match official, goalpost, crossbar or corner flagpost and remains on the field of play."),
    ],
    10: [
        ("1. Goal scored", 93, "A goal is scored when the whole of the ball passes over the goal line, between the goalposts and under the crossbar, provided that no offence has been committed by the team scoring the goal."),
        ("2. Kicks from the penalty mark", 95, "Kicks from the penalty mark are taken after the match has ended. Only eligible players who are on the field of play or temporarily off the field at the end of the match are allowed to take kicks."),
    ],
    11: [
        ("1. Offside position", 99, "A player is in an offside position if: any part of the head, body or feet is in the opponents' half (excluding the halfway line) and any part of the head, body or feet is nearer to the opponents' goal line than both the ball and the second-last opponent."),
        ("2. Offside offence & deliberate play", 101, "A player in an offside position at the moment the ball is played or touched by a team-mate is only penalised on becoming involved in active play by: interfering with play, interfering with an opponent, or gaining an advantage by playing the ball or interfering with an opponent when it has rebounded or been deflected off the goalpost, crossbar, match official or an opponent, or been deliberately saved by any opponent. A player in an offside position receiving the ball from an opponent who deliberately played the ball, including by deliberate handball, is not considered to have gained an advantage, unless it was a deliberate save by any opponent."),
        ("3. No offence", 103, "There is no offside offence if a player receives the ball directly from: a goal kick, a throw-in, or a corner kick."),
    ],
    12: [
        ("1. Direct free kick - Handball", 107, "It is an offence if a player: deliberately touches the ball with their hand/arm, for example moving the hand/arm towards the ball; touches the ball with their hand/arm when it has made their body unnaturally bigger. A player is considered to have made their body unnaturally bigger when the position of their hand/arm is not a consequence of, or justifiable by, the player's body movement for that specific situation. Scores in the opponents' goal directly from their hand/arm, even if accidental, or immediately after the ball has touched their hand/arm, even if accidental."),
        ("2. Direct free kick - Fouls", 109, "A direct free kick is awarded if a player commits any of the following offences against an opponent in a manner considered by the referee to be careless, reckless or using excessive force: charges, jumps at, kicks or attempts to kick, pushes, strikes or attempts to strike, tackles or challenges, trips or attempts to trip."),
        ("3. Denial of an obvious goal-scoring opportunity (DOGSO)", 113, "Where a player commits an offence against an opponent which denies an obvious goal-scoring opportunity and the referee awards a penalty kick, the offender is cautioned if the offence was an attempt to play the ball or a challenge for the ball; in all other circumstances (e.g. holding, pulling, pushing, no possibility to play the ball etc.), the offending player must be sent off (red card). Outside the penalty area, denying an obvious goal-scoring opportunity always results in a sending-off (red card)."),
        ("4. Stopping a promising attack (SPA)", 115, "A player must be cautioned (yellow card) if they commit a foul that stops a promising attack (SPA), unless the referee awards a penalty kick for an offence which was an attempt to play the ball or challenge for the ball."),
        ("5. Indirect free kick - Goalkeeper handling", 117, "An indirect free kick is awarded if a goalkeeper, inside their penalty area: initiates or touches the ball with the hand/arm after it has been deliberately kicked to the goalkeeper by a team-mate (backpass rule), or touches the ball with the hand/arm directly from a throw-in taken by a team-mate."),
    ],
    13: [
        ("1. Types of free kick", 121, "Direct and indirect free kicks are awarded to the opposing team of a player, substitute, substituted or sent-off player, or team official guilty of an offence. The referee indicates an indirect free kick by raising their arm above the head."),
        ("2. Wall distance and procedure", 123, "All opponents must be at least 9.15 m (10 yds) from the ball until it is in play. Where three or more defending team players form a 'wall', all attacking team players must remain at least 1 m (1 yd) from the 'wall' until the ball is in play; if an attacking player is within 1 m, an indirect free kick is awarded to the defending team."),
    ],
    14: [
        ("1. Procedure", 127, "A penalty kick is awarded if a player commits a direct free kick offence inside their penalty area. The ball must be stationary on the penalty mark. The player taking the penalty kick must be clearly identified. The defending goalkeeper must remain on the goal line, facing the kicker, between the goalposts, with at least part of one foot touching or in line with the goal line until the ball is kicked."),
        ("2. Offences and sanctions", 129, "Once the referee has signalled for a penalty kick to be taken, the kick must be taken. Feinting to kick the ball once the kicker has completed the run-up is considered an infringement of Law 14 and is an act of unsporting behaviour for which the kicker must be cautioned (yellow card), and play restarts with an indirect free kick."),
    ],
    15: [
        ("1. The Throw-in procedure", 133, "A throw-in is awarded to the opponents of the player who last touched the ball when the whole of the ball passes over the touchline. At the moment of delivering the ball, the thrower must: face the field of play, have part of each foot on the touchline or on the ground outside the touchline, throw the ball with both hands from behind and over the head. A goal cannot be scored directly from a throw-in; if the ball enters the opponents' goal directly, a goal kick is awarded; if the ball enters the thrower's goal directly, a corner kick is awarded."),
    ],
    16: [
        ("1. The Goal Kick procedure", 137, "A goal kick is awarded when the whole of the ball passes over the goal line, on the ground or in the air, having last touched a player of the attacking team, and a goal is not scored. The ball must be stationary and is kicked from any point within the goal area by a player of the defending team. The ball is in play when it is kicked and clearly moves. A goal can be scored directly from a goal kick against the opposing team; if the ball enters the kicker's goal directly, a corner kick is awarded to the opponents."),
    ],
    17: [
        ("1. The Corner Kick procedure", 141, "A corner kick is awarded when the whole of the ball passes over the goal line, having last touched a player of the defending team, and a goal is not scored. The ball must be placed in the corner area nearest to the point where the ball passed over the goal line. The ball is in play when it is kicked and clearly moves; it does not need to leave the corner area. A goal can be scored directly from a corner kick against the opposing team; if the ball directly enters the kicker's goal, a corner kick is awarded to the opponents."),
    ],
}


async def main():
    print("Preparing Law chunks from IFAB Statutory Texts and Curated Situations...")
    chunks: list[LawChunk] = []

    # 1. Add core statutory texts for Laws 1-17
    for law_num, sections in CORE_LAW_TEXTS.items():
        law_title = LAW_TITLES.get(law_num, f"Law {law_num}")
        for idx, (sec_path, page, text) in enumerate(sections, 1):
            chunk_id = f"law{law_num}-s{idx}-001"
            chunks.append(
                LawChunk(
                    chunk_id=chunk_id,
                    law_number=law_num,
                    law_title=law_title,
                    section_path=sec_path,
                    edition="2026/27",
                    page=page,
                    source="IFAB Laws of the Game",
                    lang="en",
                    clean_text=text,
                    text_for_embedding=f"Law {law_num} ({law_title}) > {sec_path}\n{text}",
                    token_count=len(text.split()),
                )
            )

    # 2. Add curated situations
    situations_file = Path("data/curated/situations.jsonl")
    if situations_file.exists():
        with open(situations_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.trim() if hasattr(line, "trim") else line.strip()
                if not line:
                    continue
                item = json.loads(line)
                law_num = item.get("law_number", item.get("primary_law", 12))
                law_title = LAW_TITLES.get(law_num, item.get("law_title", f"Law {law_num}"))
                sit_id = item["id"]
                situation = item["situation"]
                summary = item["answer_summary"]
                full_text = f"Situation: {situation}\nOfficial ruling & interpretation: {summary}"
                chunks.append(
                    LawChunk(
                        chunk_id=f"sit-{sit_id}",
                        law_number=law_num,
                        law_title=law_title,
                        section_path=f"Curated Match Situations > {situation[:40]}...",
                        edition="2026/27",
                        page=100 + law_num,
                        source="IFAB Laws of the Game / PlayRef Match Cases",
                        lang="en",
                        clean_text=full_text,
                        text_for_embedding=f"Law {law_num} ({law_title}) > Match Situation\n{full_text}",
                        token_count=len(full_text.split()),
                    )
                )

    print(f"Total chunks assembled: {len(chunks)} across {len(set(c.law_number for c in chunks))} Laws.")

    # Save to data/processed/chunks.jsonl
    out_file = Path("data/processed/chunks.jsonl")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk.model_dump(), ensure_ascii=False) + "\n")
    print(f"Saved {len(chunks)} chunks to {out_file}")

    # Index into Qdrant
    print("Embedding and indexing into Qdrant...")
    indexed_count = await index_chunks(chunks, batch_size=32, recreate=True)
    print(f"Successfully indexed {indexed_count} chunks into Qdrant collection '{settings.qdrant_collection}'!")


if __name__ == "__main__":
    asyncio.run(main())

