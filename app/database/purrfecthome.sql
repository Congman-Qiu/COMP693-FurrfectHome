DROP SCHEMA IF EXISTS pgtracker;

CREATE DATABASE `pgtracker`;

use pgtracker;

CREATE TABLE config (
	config_id INT NOT NULL AUTO_INCREMENT, 
	config_type VARCHAR(100) NULL, 
	config_value VARCHAR(100) NULL,
	PRIMARY KEY (`config_id`)
);

CREATE TABLE `department` (
  `department_id` 	int 		NOT NULL AUTO_INCREMENT,
  `department_name` varchar(50) NULL,
  PRIMARY KEY (`department_id`)
);

CREATE TABLE `user` (
  `user_id` 		int 			NOT NULL AUTO_INCREMENT,
  `email` 			varchar(100) 	NOT NULL,
  `user_type` 		varchar(25) 	NOT NULL,
  `password` 		varchar(100) 	NOT NULL,
  `department_id` 	int 			NULL,
  `is_active` 		bit 			NULL,
  `is_approved` 	bit 			NULL,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `user_department` 		FOREIGN KEY (`department_id`) REFERENCES `department` (`department_id`)
);

CREATE TABLE `supervisor` (
  `supervisor_id` 	int 		NOT NULL AUTO_INCREMENT,
  `user_id` 		int 		NOT NULL,
  `first_name` 		varchar(25) NOT NULL,
  `last_name` 		varchar(25) NOT NULL,
  `phone` 			varchar(25) DEFAULT NULL,
  PRIMARY KEY (`supervisor_id`),
  KEY `user_idx` (`user_id`),
  CONSTRAINT `user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
);



CREATE TABLE `student` (
  `student_id` 			int 		NOT NULL AUTO_INCREMENT,
  `user_id` 			int 		NOT NULL,
  `student_first_name` 	varchar(50) NOT NULL,
  `student_last_name` 	varchar(50) NOT NULL,
  `enrolment_date` 		DATE 		NULL,
  `address` 			varchar(500) NULL,
  `phone` 				varchar(25) NULL,
  `study_type` 			varchar(100) NULL,
  `thesis_title` 		varchar(500) NULL,
  PRIMARY KEY (`student_id`),
  CONSTRAINT `student_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
);

CREATE TABLE scholarship (
  `scholarship_id`    	int          	primary key NOT NULL AUTO_INCREMENT,
  `student_id`        	int          	NOT NULL,
  `scholarship_name`  	varchar(100) 	NULL,
  `value`             	DECIMAL(10,2) 	NULL,
  `tenure`			  	VARCHAR(100) 	NULL,
  `end_date`          	DATE         	NULL,
  `is_active`			BIT				NULL,	
  CONSTRAINT `student_scholarship` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`)
);

CREATE TABLE employment (
  employment_id 	int 			primary key NOT NULL AUTO_INCREMENT,
  student_id 		int 			NOT NULL,
  employment_type 	varchar(100) 	NULL,
  supervisor_name 	varchar(100) 	NULL,
  hours_per_week 	decimal(19,2) 	NULL,
  is_active			bit				NULL,
  CONSTRAINT `employment_student` 	FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`)
);

CREATE TABLE student_supervisor (
  student_id 		INT NOT NULL,
  supervisor_id 	INT NOT NULL,
  supervisor_type 	VARCHAR(50) NULL,
  is_active 		BIT NULL,
  PRIMARY KEY (student_id, supervisor_id),
  FOREIGN KEY(student_id) 		REFERENCES student (student_id),
  FOREIGN KEY(supervisor_id) 	REFERENCES supervisor (supervisor_id)
);

CREATE TABLE `chair` (
  `chair_id` 	int NOT NULL AUTO_INCREMENT,
  `user_id` 	int NOT NULL,
  `is_active`	bit NULL,
  PRIMARY KEY (`chair_id`),
  CONSTRAINT chair_user FOREIGN KEY (user_id) REFERENCES user (user_id)
);

CREATE TABLE `convenor` (
  `convenor_id` 	int NOT NULL AUTO_INCREMENT,
  `user_id` 		int NOT NULL,
  `department_id` 	int NOT NULL,
  `first_name` 		varchar(50) NULL,
  `last_name` 		varchar(50) NOT NULL,
  PRIMARY KEY (`convenor_id`),
  CONSTRAINT convenor_user FOREIGN KEY (user_id) REFERENCES user (user_id),
  CONSTRAINT convenor_department FOREIGN KEY (department_id) REFERENCES department (department_id)
);

CREATE TABLE `administrator` (
  `administrator_id` 	int NOT NULL AUTO_INCREMENT,
  `user_id` 			int NOT NULL,
  PRIMARY KEY (`administrator_id`),
  CONSTRAINT administrator_user FOREIGN KEY (user_id) REFERENCES user (user_id)
);

CREATE TABLE form_status (
	form_status_id			INT	PRIMARY KEY NOT NULL AUTO_INCREMENT,
    status					VARCHAR(50) NULL
);

CREATE TABLE form (
  form_id 					INT 		PRIMARY KEY NOT NULL AUTO_INCREMENT,
  form_status_id			INT	 		NOT NULL,
  year 						INT 		NULL,
  month 					VARCHAR(10) NULL,
  created_user_id 			INT 		NOT NULL,
  created_date 				DATE 		NOT NULL,
  current_user_id 			INT 		NOT NULL,
  current_section 			VARCHAR(2) 	NULL,
  status_updated_date 		DATE 		NOT NULL,
  is_current 				BIT 		NULL,
  is_student_submitted		BIT			NULL,
  is_supervisor_approved	BIT			NULL,  
  is_convenor_submitted		BIT			NULL,
  is_chair_completed		BIT			NULL,
  is_admin_completed		BIT			NULL,
  is_active 				BIT 		NULL,
  CONSTRAINT student_form_fk FOREIGN KEY (created_user_id) REFERENCES student (user_id),
  CONSTRAINT user_form_fk FOREIGN KEY (current_user_id) REFERENCES user (user_id),
  CONSTRAINT form_status_form_fk FOREIGN KEY (form_status_id) REFERENCES form_status (form_status_id)
);

CREATE TABLE question (
  question_id 			INT 			PRIMARY KEY NOT NULL AUTO_INCREMENT,
  section_id			INT 			NOT NULL,
  field_label_name 		VARCHAR(500)	NULL,	
  field_label_value 	VARCHAR(500)	NULL,
  field_type 			VARCHAR(25)		NULL,
  is_active 			BIT 			NULL	
);

CREATE TABLE field_option (
  field_option_id 		INT 		PRIMARY KEY NOT NULL AUTO_INCREMENT,
  field_option_value 	INT 		NULL,
  field_option_text 	VARCHAR(50) NULL,
  is_active 			BIT 		NULL
);

CREATE TABLE question_field_option (
	question_id			INT	NULL,
    field_option_id		INT NULL,
    FOREIGN KEY(question_id) 		REFERENCES question (question_id),
    FOREIGN KEY(field_option_id) 	REFERENCES field_option (field_option_id)
);

CREATE TABLE answer (
  form_id 				INT 			NOT NULL,
  question_id 			INT 			NOT NULL,
  answer_value 			VARCHAR(100) 	NULL,
  answered_by 			INT 			NOT NULL,
  answer_group			INT				NULL,
  answered_date 		DATE 			NOT NULL,
  sequence				INT				NULL,
  FOREIGN KEY(form_id) 		REFERENCES form (form_id),
  FOREIGN KEY(question_id) 	REFERENCES question (question_id)
);

CREATE TABLE notification_type (
	notification_type_id	INT	PRIMARY KEY NOT NULL AUTO_INCREMENT,
    notification_type		VARCHAR(25)
);

CREATE TABLE notification (
	notification_id			INT 			PRIMARY KEY NOT NULL AUTO_INCREMENT,
    notification_type_id	INT				NULL,
    user_id					INT 			NULL,
    created_date			DATE			NULL,
    message					VARCHAR(255)	NULL,
    is_read					BIT				NULL,
    is_active				BIT				NULL,
    FOREIGN KEY(user_id) 				REFERENCES user (user_id),
    FOREIGN KEY(notification_type_id) 	REFERENCES notification_type (notification_type_id)
);

CREATE TABLE workflow (
	workflow_id		INT 			PRIMARY KEY NOT NULL AUTO_INCREMENT,
    form_id			INT				NOT NULL,
    section_id 		INT				NOT NULL, 
    state			VARCHAR(25) 	NULL, 
    created_date	DATETIME		NULL, 
    created_by		INT				NOT NULL,
    FOREIGN KEY(created_by) 			REFERENCES user (user_id),
    FOREIGN KEY(form_id) 			REFERENCES form (form_id)
);