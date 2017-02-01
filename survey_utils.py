from enum import Enum


TLX_COMPONENTS = [
    "mental",
    "physical",
    "temporal",
    "performance",
    "effort",
    "frustration",
]
ExperimentType = Enum("ExperimentType", "Onboard Spirit Combined")


class User(object):
    count = 0

    def __init__(self, name, age, gender, teleop, flying):
        self.id_ = User.count
        self.name = name
        self.age = age
        self.teleop = teleop
        self.flying = flying
        User.count += 1
        self.experiments = []

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"User({self.id}, {self.name})"


class Experiment(object):
    def __init__(self, user, type_, survey, tlx):
        self.user = user
        self.type_ = type_
        self.survey = survey
        self.tlx = tlx

    def __repr__(self):
        return f"Experiment({self.type_}, {self.user.id})"


class TlxComponent(object):
    def __init__(self, name, description):
        self.code = name.split()[0].lower()
        self.name = name
        self.description = description
        self.score = 0
        self.weight = 0

    @property
    def weighted_score(self):
        return self.score * self.weight

    def __repr__(self):
        return f"Component({self.code}, {self.weighted_score})"


class Tlx(object):
    _components = {
        "Mental Demand / 知的・知覚的要求": "(Low to High) How mentally demanding was the task? / どの程度の知的、知覚的活動（考える、決める、計算する、記憶する、見る、など）を必要としましたか？課題はやさしかったですか、難しかったですか？単純でしたか、複雑でしたか？正確さが求められましたか、おおざっぱでよかったですか？",
        "Physical Demand / 身体的要求": "(Low to High) How physically demanding was the task? / どの程度の身体的活動（押す、引く、回す、制御する、動き回るなど）を必要としましたか？　作業がラクでしたか、キツかったですか？　ゆっくりできましたか、キビキビやらなければなりませんでしたか？　休み休みできましたか、働きづめでしたか？",
        "Temporal Demand / タイムプレッシャー": "(Low to High) How hurried or rushed was the pace of the task? / 仕事のペースや課題が発生する頻度のために感じる時間的切迫感はどの程度でしたか？　ペースはゆっくりとして余裕のあるものでしたか、それとも速くて余裕のないものでしたか？",
        "Performance / 作業成績の悪さ": "(Perfect to Failure) How successful were you in accomplishing what you were asked to do? / 作業指示者（またはあなた自身）によって設定された課題の目標を、どの程度達成できたと思いますか？　目標の達成に関して、自分の作業成績にどの程度満足していますか？",
        "Effort / 努力": "(Low to High) How hard did you have to work to accomplish your level of performance? / 作業成績のレベルを達成・維持するために、精神的・身体的にどの程度いっしょうけんめいに作業しなければなりませんでしたか？",
        "Frustration / フラストレーション": "(Low to High) How insecure, discouraged, irritated, stressed, and annoyed were you? / 作業中に、不安感、落胆、イライラ、ストレス、悩みをどの程度感じましたか？　あるいは逆に安心感、満足感、充足感、楽しさ、リラックスをどの程度感じましたか？",
    }

    def __init__(self):
        self.components = {}
        for name, description in self._components.items():
            component = TlxComponent(name, description)
            self.components[component.code] = component

    def __repr__(self):
        return "<Tlx()>"


class Question(object):
    def __init__(self, code, description):
        self.code = code
        self.description = description
        self.score = 1

    def __repr__(self):
        return f"Question({self.code}, {self.score})"


class Survey(object):
    _questions = {
        "pos_under": "Your understanding of the position of the drone",
        "orient_under": "Your understanding of the orientation of the drone",
        "spacial_under": "Your understanding of the spacial relationship between the drone and the target",
        "pos_control": "Your control of the position of the drone",
        "orient_control": "Your control of the orientation of the drone",
        "spacial_control": "Your ability to stay above the target",
    }

    def __init__(self):
        self.questions = {}
        for code, description in self._questions.items():
            question = Question(code, description)
            self.questions[code] = question

    def __repr__(self):
        return "<Survey()>"
