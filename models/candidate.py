from __future__ import annotations

class Candidate(object):
    """
    提供 to_dict 與 from_dict 方法，方便用於物件與字典的轉換
    """

    def __init__(self, _id, name, gender, age, platform, platform_code, cell_phone, email, address,
        edu_level, edu_status, edu_school,edu_department,wanted_job_titles, wanted_job_types,
        wanted_job_locations,working_months, work_experiences, work_experience_list,
        computer_expertises, languages):
        self._id = _id
        self.name = name
        self.gender = gender
        self.age = age
        self.platform = platform
        self.platform_code = platform_code
        self.cell_phone = cell_phone
        self.email = email
        self.address = address
        self.edu_level = edu_level
        self.edu_status = edu_status
        self.edu_school = edu_school
        self.edu_department = edu_department
        self.wanted_job_titles = wanted_job_titles
        self.wanted_job_types = wanted_job_types
        self.wanted_job_locations = wanted_job_locations
        self.working_months = working_months
        self.work_experiences = work_experiences
        self.work_experience_list = work_experience_list
        self.computer_expertises = computer_expertises
        self.languages = languages

