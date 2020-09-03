console.log(window.location.origin);

function ready() {
    console.log("ready");
    document.getElementById("course_id").addEventListener("change", () => {
                                                        getSubjects(),
                                                        fetchSections()
                                                    });

    function fetchSections() {
        console.log("fetchSections");
        const courseId = document.getElementById("course_id").value;
        data = JSON.stringify({'courseId': courseId});
        const xhr = new XMLHttpRequest();
        if (!window.location.origin) {
          window.location.origin = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
        }
        xhr.open("POST", window.location.origin + "/sms/admin/section/fetch/");
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onload = function() {
            const secContainer = document.getElementById("section_list");
            if (this.status == 200) {
                const sections = JSON.parse(this.responseText);
                let htmlBlock = "<select class='form-control' name='section' id='section'>";
                if (sections.length > 0) {
                    sections.forEach(section=> {
                       htmlBlock += "<option value='"+ section.pk +"'>"+ section.fields.section_name +"</option>";
                    });
                    htmlBlock += "</select>";
                }
                else {
                    htmlBlock += "<p class='bg-warning text-center rounded p-1'>There are no section entry on this course in the selected school year.</p>"
                }
                secContainer.innerHTML = htmlBlock;
            }
            else {
                htmlBlock = "<p>Unable to fetch section records.</p>";
                secContainer.innerHTML = htmlBlock;
            }

        };
        xhr.send(data);

    }

    function getSubjects() {
        console.log("getSubjects");
        var id = document.getElementById("course_id").value;
        var xhr = new XMLHttpRequest();
        var data = JSON.stringify({'course_id': id});

        document.getElementById("course_subjects").innerHTML = '';

        if (!window.location.origin) {
          window.location.origin = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
        }
        xhr.open("POST", window.location.origin + "/sms/admin/ajax/getsubjects/", true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function() {
            let htmlBlock = "<div class='card card-primary'><div class='card-header'><h3 class='card-title'>Subjects</h3></div><div class='card-body'>";
            if (this.status == 200) {
                let courseSubjects = JSON.parse(this.responseText);
                if (courseSubjects.length > 0) {
                    courseSubjects.forEach(renderSubjects);

                    function renderSubjects(subject) {
                        htmlBlock += '<div class="form-check"><input type="checkbox" name="subject_list[]" id="subject_'+subject.fields.subject_name +
                        '" value="'+subject.pk+'">' +
                        '<label for="subject_'+subject.fields.subject_name+'" class="ml-1">' +
                        subject.fields.subject_name + '</label></div>'
                    }
                }
                else {
                    htmlBlock += "<p class='bg-warning text-center rounded p-1'>There are no subjects offered under the selected course.</p>"
                }

            }
            else {
                htmlBlock += "<p class='bg-warning text-center rounded p-1'>Unable to retrieve course subjects.</p>"
            }
            htmlBlock += '</div></div>'
            document.getElementById("course_subjects").innerHTML = htmlBlock;
        };
        xhr.send(data);
    }
}

window.addEventListener("load", ready);
