console.log("staff.js");
function ready() {
    console.log("staff document ready")
    document.getElementById("btn_fetch_students").addEventListener("click", fetchStudents);
                document.getElementById("btn_save_attendance").addEventListener("click", saveAttendance);
                document.getElementById("school_year").addEventListener("change", resetStudentList);
                document.getElementById("staff_subject").addEventListener("change", () => {
                                                                                resetStudentList(),
                                                                                fetchSections()
                                                                            });

    function fetchSections() {
        console.log("fetching sections");
        const sectionSel = document.getElementById("staff_subject");
        const courseId = sectionSel.options[sectionSel.selectedIndex].getAttribute("data-course");
        console.log(courseId);
        data = JSON.stringify({'courseId': courseId});
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "{% url 'ajax-staff-fetch-sections' %}");
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onload = function() {
            const secContainer = document.getElementById("section_list");
            if (this.status == 200) {
                console.log("status 200");
                const sections = JSON.parse(this.responseText);
                console.log(sections);
                let htmlBlock = "<label for='school_year'>Section</label><select class='form-control' name='section' id='section'>";
                if (sections.length > 0) {
                    sections.forEach(section=> {
                       htmlBlock += "<option value='"+ section.pk +"'>"+ section.fields.section_name +"</option>";
                    });
                    htmlBlock += "</select>";
                    document.getElementById("btn_fetch_students").removeAttribute("disabled", "disabled");
                }
                else {
                    htmlBlock += "<p class='bg-warning text-center rounded p-1'>There are no section entry on this course in the selected school year.</p>"
                }
                secContainer.innerHTML = htmlBlock;
            }
            else {
                htmlBlock = "<p>Unable to fetch section records.</p>";
                studContainer.innerHTML = htmlBlock;
            }

        };
        xhr.send(data);

    }

    function resetStudentList() {
        document.getElementById("student_list").innerHTML = "";
        document.getElementById("btn_save_attendance").setAttribute("disabled", "disabled");
    }

    function fetchStudents(e) {
        e.preventDefault();
        console.log("fetching students... by userid:" + {{user.id}});

        <!-- Get field values for ajax parameters -->
        const staff_id = {{user.id}}
        const subject_id = document.getElementById("staff_subject").value;
        const school_year_id = document.getElementById("school_year").value;

        <!-- JSON stringify data parameters -->
        let data = JSON.stringify({'staff_id': staff_id, 'subject_id': subject_id, 'school_year_id': school_year_id});

        const xhr = new XMLHttpRequest()
        xhr.open("POST", "{% url 'ajax-staff-fetch-students' %}");
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onload = function() {
            const studContainer = document.getElementById("student_list");
            let htmlBlock = "<div class='form-group'>";
            if (this.status == 200) {
                const students = JSON.parse(this.responseText);
                if (students.length > 0) {
                    students.forEach(student => {
                       htmlBlock += "<div class='form-control'><label><input type='checkbox' class='student mr-1' name='student[]' id='student' value='" +
                       student.pk+"'></input>" + student.fields.first_name+ " " + student.fields.middle_initial + ". " +
                       student.fields.last_name +"</label></div>";
                    });
                    document.getElementById("btn_save_attendance").removeAttribute("disabled", "disabled");
                }
                else {
                    htmlBlock += "<p class='bg-warning text-center rounded p-1'>There are no students enrolled on this subject in the selected school year.</p>"
                }
                htmlBlock += "</div>";
                studContainer.innerHTML = htmlBlock;
            }
            else {
                htmlBlock = "<p>Unable to fetch student records.</p>";
                studContainer.innerHTML = htmlBlock;
            }

        };
        xhr.send(data);
    }

    function saveAttendance() {
        const xhr = new XMLHttpRequest();
        <!--  Convert NodeList Object to an array to be processed using map function -->
        const student_list = Array.prototype.slice.call(document.getElementsByName("student[]"));
        const present_students = student_list.map(function (student) {
                                        return student.value;
                                    });

        let id_list = present_students;

        xhr.open("POST", "{% url 'ajax-save-student-attendance' %}");
        xhr.setRequestHeader("Content-Type", "application/json");

        xhr.onload = function() {
            if (this.status == 200) {
                console.log("Saving attendance successful");
                const status = JSON.parse(this.responseText);
                console.log(status.status);
            }
            else {
                console.log("Error: 400");
            }
            <!--Redirect user to main dashboard for alert message status-->
            location.href = "/sms/staff/dashboard/attendance";
        };

        const subject_id = document.getElementById("staff_subject").value;
        const school_year = document.getElementById("school_year").value;

        const data = JSON.stringify({'id_list':id_list, 'subject_id':subject_id, 'school_year_id':school_year});

        xhr.send(data);
    }
}

window.addEventListener("load", ready);