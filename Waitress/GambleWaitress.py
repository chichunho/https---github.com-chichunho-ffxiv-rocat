from dataclasses import dataclass
from itertools import combinations

from models.CommandRequest import CommandRequest
from utils.Embed import SixEmbed


@dataclass
class ChoiceStat:
    choice: tuple[int, int, int]
    min_return: int
    max_return: int
    avg_return: float
    exp_return: float


class GambleWaitress:
    scores: dict[int, int] = {
        6: 10000,
        7: 36,
        8: 720,
        9: 360,
        10: 80,
        11: 252,
        12: 108,
        13: 72,
        14: 54,
        15: 180,
        16: 72,
        17: 180,
        18: 119,
        19: 36,
        20: 306,
        21: 1080,
        22: 144,
        23: 1800,
        24: 3600,
    }

    choices: list[tuple[int, int, int]] = [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    ]

    def __init__(self):
        pass

    async def start(self, request: CommandRequest):
        input_map = request.args["input_map"]
        global_cand = request.args["global_cand"]
        stats: list[ChoiceStat] = []
        for choice in self.choices:
            eles: list[str] = []

            for idx in choice:
                eles.append(input_map[idx])

            min_return, max_return, avg_return, exp_return = self.get_stat(eles, global_cand)

            choice_stat = ChoiceStat(
                choice,
                min_return,
                max_return,
                avg_return,
                exp_return,
            )

            stats.append(choice_stat)

        stats = sorted(stats, key=lambda s: s.exp_return, reverse=True)

        embed = SixEmbed(stats[0].choice)

        await request.ctx.message.reply(content=embed.message())

    def get_norm_score_dist(
        self,
        cands: list[int],
        fixed: list[int],
    ) -> dict[int, float]:
        norm_score_dist: dict[int, float] = {}

        for c in combinations(cands, 3 - len(fixed)):
            key = sum(c) + sum(fixed)
            score = self.scores[key]
            if score not in norm_score_dist:
                norm_score_dist[score] = 1
            else:
                norm_score_dist[score] += 1

        freq_sum = float(sum(norm_score_dist.values()))

        for score in norm_score_dist:
            norm_score_dist[score] /= freq_sum

        return norm_score_dist

    def get_expected_value(self, norm_score_dist: dict[int, float]):
        expected_value: float = 0
        for score, prob in norm_score_dist.items():
            expected_value += score * prob
        return expected_value

    def get_stat(
        self,
        eles: list[str],
        global_cand: list[int],
    ) -> tuple[int, int, float, float, float]:
        fixed: list[int] = []

        for ele in eles:
            if ele != ".":
                fixed.append(int(ele))

        norm_score_dist = self.get_norm_score_dist(global_cand, fixed)
        expected_value = self.get_expected_value(norm_score_dist)

        return (
            min(norm_score_dist.keys()),
            max(norm_score_dist.keys()),
            sum(norm_score_dist.keys()) / float(len(norm_score_dist)),
            expected_value,
        )
