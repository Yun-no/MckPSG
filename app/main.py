from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


class Species(BaseModel):
    name: str
    cal_in: int
    cal_out: int
    cal_left: int | None
    level: int
    eats_info: str
    eats: list[str] | None


class ValidateResult():
    def __init__(self):
        self.passed = 1
        self.issues = []


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/validate")
async def check_species(spec_list: list[Species]):
    r = ValidateResult()
    r.passed = 1
    name_list = [[] for i in range(4)]
    for spec in spec_list:
        spec.eats = spec.eats_info.split(',')
        name_list[spec.level - 1].append(spec.name.lower())
        if spec.cal_out is None or spec.cal_out < 1:
            r.passed = 0
            r.issues.append(f"{spec.name} has no invalid cal_out!")
    for spec in spec_list:
        if spec.level < 4:
            ###Need to have eats
            eat_list = spec.eats
            if not eat_list:
                r.passed = 0
                r.issues.append(f"{spec.name} has no eats!")
            else:
                for food in eat_list:
                    if food.lower() not in name_list[spec.level]:
                        r.passed = 0
                        r.issues.append(f"{spec.name} eats {food} that is not in next eco system level!")
    return r


@app.post("/check")
async def check_species(spec_list: list[Species]):
    apex = []
    predator = []
    herbivore = []
    producer = []
    for spec in spec_list:
        spec.eats = [x.strip() for x in spec.eats_info.split(',')]
        spec.cal_left = spec.cal_out
        if spec.level == 1:
            apex.append(spec)
        elif spec.level == 2:
            predator.append(spec)
        elif spec.level == 3:
            herbivore.append(spec)
        elif spec.level == 4:
            producer.append(spec)
    apex.sort(key=lambda x: x.cal_out, reverse=True)
    predator.sort(key=lambda x: x.cal_out, reverse=True)
    herbivore.sort(key=lambda x: x.cal_out, reverse=True)
    # herbivore eats producer##
    message = []

    def check_eat_chain(eater, supplier):
        for a in eater:
            cal_needed = a.cal_in
            foods = a.eats
            food_list = [s for s in supplier if s.name in foods]
            food_list.sort(key=lambda x: x.cal_left, reverse=True)
            i = 0
            while i < len(food_list) and cal_needed > 0:
                # check if next food has same cal_left, if so eat evenly
                if i < len(food_list) - 1 and food_list[i].cal_left == food_list[i + 1].cal_left:
                    cal_needed_half = cal_needed // 2
                    if cal_needed_half <= food_list[i].cal_left:
                        food_list[i].cal_left = food_list[i].cal_left - cal_needed_half
                        food_list[i + 1].cal_left = food_list[i + 1].cal_left - cal_needed_half
                        message.append(
                            f"{a.name} eats evenly between {food_list[i].name} and {food_list[i + 1].name}, consume {cal_needed} cal and feed.")
                        message.append(
                            f"{food_list[i].name} and {food_list[i + 1].name} have {food_list[i].cal_left} cal left.")
                        cal_needed = 0
                        break
                    else:
                        message.append(
                            f"{a.name} eats evenly between {food_list[i].name} and {food_list[i + 1].name}, consume {food_list[i].cal_left*2} cal and need more.")
                        cal_needed -= food_list[i].cal_left * 2
                        food_list[i].cal_left = food_list[i + 1].cal_left = 0
                        message.append(
                            f"{food_list[i].name} and {food_list[i + 1].name} extinct.")
                        i += 2
                else:
                    if cal_needed <= food_list[i].cal_left:
                        food_list[i].cal_left = food_list[i].cal_left - cal_needed
                        message.append(
                            f"{a.name} eats {food_list[i].name}, consume {cal_needed} cal and feed.")
                        message.append(
                            f"{food_list[i].name} have {food_list[i].cal_left} cal left.")
                        cal_needed = 0
                        break
                    else:
                        message.append(
                            f"{a.name} eats {food_list[i].name}, consume {food_list[i].cal_left} cal and need more.")
                        cal_needed -= food_list[i].cal_left
                        food_list[i].cal_left = 0
                        message.append(
                            f"{food_list[i].name} extinct.")
                        i += 1
            if cal_needed > 0:
                message.append(
                    f"{a.name} still needs {cal_needed} cal and starved to death.")

    check_eat_chain(herbivore, producer)
    check_eat_chain(predator, herbivore)
    check_eat_chain(apex, predator)
    return message
