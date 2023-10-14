class Form():
    def __init__(self):
        self.form_id = None
        self.form_status_id = None
        self.year = None
        self.month = None
        self.created_user_id = None
        self.created_date = None
        self.current_user_id = None
        self.current_section = None
        self.status_updated_date = None
        self.is_current = None
        self.is_student_submitted = None
        self.is_supervisor_approved = None
        self.is_convenor_submitted = None
        self.is_admin_completed = None
        self.is_chair_completed = None
        self.is_active = None
        self.student_first_name = None
        self.student_last_name = None
        self.is_section_f_filled = None


class SectionA():
    def __init__(self):
        self.form_id = None


class SectionD():
    def __init__(self):
        self.objective_changed = None
        self.comments = None
        self.date = None
        self.res_obj_list = []
        self.current_res_obj_list = []
        self.next_res_obj_list = []
        self.achievements_list = []
        self.expenditure_list = []


class SupervisorAnswer():
    def __init__(self):
        self.supervisor_name = None
        self.supervisor_type = None
        self.supervisor_id = None
        self.performance_questions = []
        self.performance_answers = []
        self.recommendation_answers = []
        self.supervisor_comment_answers = []
        self.supervisor_date_answers = []


class SectionE():
    def __init__(self):
        self.supervisor_answers_list = []
        self.convenor_date_answers = []
        self.highlight_answers = []
        self.color_rating_answers = []
        self.convenor = None

        