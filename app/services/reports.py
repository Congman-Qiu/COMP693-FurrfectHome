from app.util import database


def getCursor():
    return database.getCursor()


# get form summary report
def get_form_summary_report(department_id=None):

    filter_query = ""

    if department_id:
        filter_query += f" WHERE d.department_id = {department_id}"

    cur = getCursor()
    cur.execute(
        f"""
		with cte as(         
		SELECT      d.department_id,
					d.department_name, 
					CONCAT(s.student_first_name, ' ', s.student_last_name) as Sname, 
					s.student_id, 
					u.user_id,
					CONCAT(MAX(CASE WHEN b.RN = 1 THEN b.first_name END), ' ', MAX(CASE WHEN b.RN = 1 THEN b.last_name END)) AS sp1,
					CONCAT(MAX(CASE WHEN b.RN = 2 THEN b.first_name END), ' ', MAX(CASE WHEN b.RN = 2 THEN b.last_name END)) AS sp2,
					CONCAT(MAX(CASE WHEN b.RN = 3 THEN b.first_name END), ' ', MAX(CASE WHEN b.RN = 3 THEN b.last_name END)) AS sp3
				FROM student s
				LEFT JOIN (SELECT ss.student_id, sup.first_name, sup.last_name
							,ROW_NUMBER()OVER(PARTITION BY ss.student_id order by ss.supervisor_type desc) as RN
				FROM student_supervisor ss 
				LEFT JOIN supervisor sup 
				ON ss.supervisor_id = sup.supervisor_id) b ON s.student_id = b.student_id
				LEFT JOIN user u on s.user_id = u.user_id
				LEFT JOIN department d on u.department_id = d.department_id
                {filter_query}
				group by 1,2,3,4,5)
		select department_id, department_name, Sname, student_id, 'PhD' as Degree, sp1, sp2, sp3,
					GROUP_CONCAT(CASE WHEN CONCAT(fa.year, ' ', fa.month) = '2022 December' THEN fa.answer_value else null END) AS 2022dstatus,
					GROUP_CONCAT(case when CONCAT(fa.year, ' ', fa.month) = '2023 June' then fa.answer_value else null end) as 2023jstatus,
					GROUP_CONCAT(case when CONCAT(fa.year, ' ', fa.month) = '2023 December' then fa.answer_value else null end) as 2023dstatus
		from cte
		LEFT JOIN (select f.form_id, f.created_user_id, year, month, a.answer_value from form f
						   LEFT JOIN (select form_id, answer_value from answer where question_id = 85) a on a.form_id = f.form_id) fa
				on fa.created_user_id = cte.user_id
		group by 1,2,3,4,5,6,7,8
		order by 1,4;
        """
    )

    students_status_list = cur.fetchall()

    return students_status_list


# get performance analysis report
def get_performance_analysis_report_list():
    cur = getCursor()
    cur.execute(
        """
        select distinct year, month from form order by 1 desc, 2 desc
        """
    )

    faculty_performance_report_list = cur.fetchall()

    return faculty_performance_report_list


# get performance analysis report
def get_performance_analysis_report(year, month):
    cur = getCursor()
    cur.execute(
        """
        select q.question_id, q.field_label_value, 
        sum(case when a.answer_value = 1 then 1 else 0 end) as 'Very Good',
        sum(case when a.answer_value = 2 then 1 else 0 end) as 'Good',
        sum(case when a.answer_value = 3 then 1 else 0 end) as 'Satisfactory',
        sum(case when a.answer_value = 4 then 1 else 0 end) as 'Unsatisfactory',
        sum(case when a.answer_value = 5 then 1 else 0 end) as 'Not Relevant',
        count(a.answer_value) as Total
        from question q
        join answer a on q.question_id = a.question_id
        join form f on a.form_id = f.form_id
        where q.question_id between 24 and 42
        and f.year = %s
		and f.month = %s
        group by q.question_id, q.field_label_value
        order by 1 asc
        """
    , (year, month,),)

    faculty_performance_list = cur.fetchall()

    return faculty_performance_list


# get performance analysis report percentage
def get_pa_report_percentage(year, month):
    cur = getCursor()
    cur.execute(
        """
        with cte as(   
        select q.question_id, q.field_label_value, count(f.form_id) as formno,
        sum(case when a.answer_value = 1 then 1 else 0 end) as 'VeryGood',
        sum(case when a.answer_value = 2 then 1 else 0 end) as 'Good',
        sum(case when a.answer_value = 3 then 1 else 0 end) as 'Satisfactory',
        sum(case when a.answer_value = 4 then 1 else 0 end) as 'Unsatisfactory',
        sum(case when a.answer_value = 5 then 1 else 0 end) as 'NotRelevant',
        count(a.answer_value) as Total
        from question q
        join answer a on q.question_id = a.question_id
        join form f on a.form_id = f.form_id
        where q.question_id between 24 and 42
        and f.year = %s
		and f.month = %s
        group by q.question_id, q.field_label_value
        order by 1 asc)
        select
        sum(VeryGood) as VeryGoodTotal, 
		round(sum(VeryGood)* 100/sum(Total),2) as VeryGoodPercent,
        sum(Good) as GoodTotal, 
		round(sum(Good)* 100/sum(Total),2) as GoodPercent,
        sum(Satisfactory) as SatisfactoryTotal,  
		round(sum(Satisfactory)* 100/sum(Total),2) as SatisfactoryPercent,
        sum(Unsatisfactory) as UnsatisfactoryTotal,  
		round(sum(Unsatisfactory)* 100/sum(Total),2) as UnsatisfactoryPercent,
        sum(NotRelevant) as NotRelevantTotal,  
		round(sum(NotRelevant)* 100/sum(Total),2) as NotRelevantPercent,
        sum(Total) as Total,
		formno
        from cte
		group by formno
        """
    , (year, month,),)

    faculty_pa_percentage_list = cur.fetchall()

    return faculty_pa_percentage_list
