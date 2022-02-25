from os import path

base_path = "/content/sample_data/f_find_great_mentors.in.txt"
base_path = "./mentorship_input_data/a_an_example.in.txt"
base_path = "./mentorship_input_data/b_better_start_small.in.txt"
base_path = "./mentorship_input_data/c_collaboration.in.txt"
base_path = "./mentorship_input_data/d_dense_schedule.in.txt"
base_path = "./mentorship_input_data/e_exceptional_skills.in.txt"
base_path = "./mentorship_input_data/f_find_great_mentors.in.txt"

input_file = open(base_path, 'r')
input_file_lines = input_file.readlines()

n_contributors = int(input_file_lines[0].split(' ')[0])
n_projects = int(input_file_lines[0].split(' ')[1])
input_file_lines = input_file_lines[1:]

print('Contributors', n_contributors, 'Projects', n_projects)

contributors = {}
line = 0
for _ in range(n_contributors):
    contributor = input_file_lines[line].split(' ')[0]
    n_skills = int(input_file_lines[line].split(' ')[1])
    line += 1
    contributors[contributor] = {}
    for __ in range(n_skills):
        skill = input_file_lines[line].split(' ')[0]
        skill_level = int(input_file_lines[line].split(' ')[1])
        line += 1

        contributors[contributor][skill] = skill_level

projects = {}
for _ in range(n_projects):
    project = input_file_lines[line].split(' ')[0]
    days = int(input_file_lines[line].split(' ')[1])
    score = int(input_file_lines[line].split(' ')[2])
    best_before = int(input_file_lines[line].split(' ')[3])
    n_roles = int(input_file_lines[line].split(' ')[4])
    line += 1
    projects[project] = {'days': days, 'score': score, 'best_before': best_before, 'roles': []}
    for __ in range(n_roles):
        skill = input_file_lines[line].split(' ')[0]
        skill_level = int(input_file_lines[line].split(' ')[1])
        line += 1
        projects[project]['roles'].append((skill, skill_level))


## LOGIC

def score_project(project, completion_time):
  extra_days = completion_time - project['best_before']
  return project['score'] - extra_days if (project['score'] - extra_days > 0) else 0


def get_min_contributor(rol, lvl, available_contributors, cforProject):
    return_contributor = None
    minLvl = None
    for contributorId, rols in available_contributors:
        if rol in rols \
                and contributorId not in cforProject \
                and lvl <= rols[rol]:
            if minLvl is None or rols[rol] < minLvl:
                minLvl = rols[rol]
                return_contributor = (contributorId, rols)
    # contributor['usedSkill'] = rol
    return return_contributor


def get_contributors_for_project(project, available_contributors):
    cforProject = []
    cforProjectId = []
    for rol in project[1]['roles']:
        contributor = get_min_contributor(rol[0], rol[1], available_contributors, cforProjectId)
        if contributor is not None:
            cforProject.append(contributor)
            cforProjectId.append(contributor[0])
        else:
            return None
    return cforProject

def evolve_dev(dev, role, ongoing_project):
    if dev[1][role[0]] == role[1]:
        dev[1][role[0]] = dev[1][role[0]]+1
    return dev


sorted_projects = [(project, project_info) for project, project_info in projects.items()]
#sorted_projects = sorted_projects.sort(key=lambda x: (x[1]['best_before']-x[1]['days'], x['score']), reverse=(False, True))

pending_projects = sorted_projects
available_contributors = [(name, cont_skills) for name, cont_skills in contributors.items()]
ongoing_projects, completed_projects = [], []
day = 0
try:
    while len(pending_projects) > 0 or len(ongoing_projects) > 0:
        pending_projects = [p for p in pending_projects if score_project(p[1], day+p[1]['days']) > 0]

        # Check if any ongoing project has finished
        completed_projects_today = []
        for ongoing_project in ongoing_projects:
            if ongoing_project['completion_day'] == day:
                completed_projects_today.append(ongoing_project)
                ongoing_project['devs'] = [evolve_dev(dev, role, ongoing_project) for dev, role in zip(ongoing_project['devs'], ongoing_project['roles'])]
                available_contributors.extend(ongoing_project['devs'])

        for completed_project_today in completed_projects_today:
            ongoing_projects.remove(completed_project_today)
        completed_projects.extend(completed_projects_today)

        # Assign pending projects
        assigned_projects = []
        for pending_project in pending_projects:
            assigned_devs = get_contributors_for_project(pending_project, available_contributors)
            if assigned_devs is None:
                continue

            assigned_projects.append(pending_project[0])
            ongoing_projects.append({
                'name': pending_project[0],
                'roles': pending_project[1]['roles'],
                'devs': assigned_devs,
                'completion_day': day + pending_project[1]['days']
            })

        pending_projects = [p for p in pending_projects if p[0] not in assigned_projects]
        day += 1
finally:
    ## OUTPUT

    executed_projects = [(p['name'], [d[0] for d in p['devs']]) for p in completed_projects]
    n_executed_projects = len(executed_projects)
    output_lines = [f"{n_executed_projects}\n"]

    for project_name, contributors in executed_projects:
        output_lines.append(f"{project_name}\n")
        output_lines.append(f"{' '.join(contributors)}\n")

    output_path = base_path.replace('_input_', '_output_').replace('.in.', '.out.')
    output_file = open(output_path, 'w')
    output_file.writelines(output_lines)
    output_file.close()
