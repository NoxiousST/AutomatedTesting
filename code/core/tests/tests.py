# tests.py
import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from ninja.testing import TestClient

from core.api import router
from core.utils import calculator, validate_password, calculate_discount


class CalculatorFunctionTest(TestCase):
    def test_addition(self):
        self.assertEqual(calculator(1, 2, "+"), 3)
        self.assertEqual(calculator(-1, -1, "+"), -2)
        self.assertEqual(calculator(0, 5, "+"), 5)

    def test_subtraction(self):
        self.assertEqual(calculator(5, 3, "-"), 2)
        self.assertEqual(calculator(-1, -1, "-"), 0)
        self.assertEqual(calculator(0, 5, "-"), -5)

    def test_multiplication(self):
        self.assertEqual(calculator(3, 4, "x"), 12)
        self.assertEqual(calculator(-1, 5, "x"), -5)
        self.assertEqual(calculator(0, 5, "x"), 0)

    def test_division(self):
        self.assertEqual(calculator(10, 2, "/"), 5)
        self.assertEqual(calculator(-10, 2, "/"), -5)
        self.assertEqual(calculator(0, 1, "/"), 0)

    def test_division_by_zero(self):
        with self.assertRaises(ValueError) as context:
            calculator(10, 0, "/")
        self.assertEqual(str(context.exception), "Cannot divide by zero")

    def test_invalid_operator(self):
        with self.assertRaises(ValueError) as context:
            calculator(10, 5, "%")
        self.assertEqual(str(context.exception), "Invalid operator")


class PasswordValidationTest(TestCase):
    def test_valid_password(self):
        self.assertTrue(validate_password("PassValid1!"))
        self.assertTrue(validate_password("StrongPassword1@"))
        self.assertTrue(validate_password("Another$Valid2"))

    def test_invalid_password_length(self):
        self.assertFalse(validate_password("Short1!"))  # Terlalu pendek
        self.assertFalse(
            validate_password("NoSpecialChar1")
        )  # Tidak ada karakter khusus

    def test_invalid_password_no_uppercase(self):
        self.assertFalse(
            validate_password("invalidpassword1!")
        )  # Tidak ada huruf besar

    def test_invalid_password_no_lowercase(self):
        self.assertFalse(
            validate_password("INVALIDPASSWORD1!")
        )  # Tidak ada huruf kecil

    def test_invalid_password_no_digit(self):
        self.assertFalse(validate_password("NoDigit!"))  # Tidak ada angka

    def test_invalid_password_no_special_char(self):
        self.assertFalse(
            validate_password("NoSpecialChar1")
        )  # Tidak ada karakter khusus


from core.models import (
    CourseMember,
    Course,
    ROLE_OPTIONS,
    Course2,
    CourseContent,
    Comment,
)


class CourseModelTest(TestCase):
    def setUp(self):
        # Menyiapkan data untuk pengujian
        self.user = User.objects.create_user(
            username="teacher1", password="password123"
        )
        self.student = User.objects.create_user(
            username="student1", password="password123"
        )
        self.course = Course.objects.create(
            name="Django for Beginners",
            description="Learn Django from scratch.",
            price=100,
            teacher=self.user,
        )

    def test_course_creation(self):
        # Menguji apakah objek Course berhasil dibuat
        self.assertEqual(self.course.name, "Django for Beginners")
        self.assertEqual(self.course.description, "Learn Django from scratch.")
        self.assertEqual(self.course.price, 100)
        self.assertEqual(self.course.teacher, self.user)

    def test_course_str(self):
        # Menguji metode __str__
        self.assertEqual(str(self.course), "Django for Beginners")

    def test_is_member(self):
        # Menguji metode is_member
        # Sebelum menambahkan anggota, harusnya False
        self.assertFalse(self.course.is_member(self.student))
        # Menambahkan anggota ke kursus
        CourseMember.objects.create(course_id=self.course, user_id=self.student)
        # Setelah menambahkan anggota, harusnya True
        self.assertTrue(self.course.is_member(self.student))


class CourseMemberModelTest(TestCase):
    def setUp(self):
        # Menyiapkan data untuk pengujian
        self.user = User.objects.create_user(
            username="teacher1", password="password123"
        )
        self.student = User.objects.create_user(
            username="student1", password="password123"
        )
        self.course = Course.objects.create(
            name="Django for Beginners",
            description="Learn Django from scratch.",
            price=100,
            teacher=self.user,
        )
        self.course_member = CourseMember.objects.create(
            course_id=self.course, user_id=self.student, roles="std"
        )

    def test_course_member_creation(self):
        # Menguji apakah objek CourseMember berhasil dibuat
        self.assertEqual(self.course_member.course_id, self.course)
        self.assertEqual(self.course_member.user_id, self.student)
        self.assertEqual(self.course_member.roles, "std")

    def test_course_member_str(self):
        # Menguji metode __str__
        self.assertEqual(str(self.course_member), f"{self.course} : {self.student}")

    def test_course_member_role_options(self):
        # Menguji pilihan peran
        self.assertIn(self.course_member.roles, dict(ROLE_OPTIONS).keys())


class UtilsTest(TestCase):
    def test_calculate_discount(self):
        self.assertEqual(calculate_discount(100, 10), 90)
        self.assertEqual(calculate_discount(200, 50), 100)
    def test_calculate_discount_invalid(self):
        with self.assertRaises(ValueError):
            calculate_discount(100, -10)
        with self.assertRaises(ValueError):
            calculate_discount(100, 110)

class CourseViewTest(TestCase):
    def setUp(self):
        # Menyiapkan data untuk pengujian
        Course2.objects.create(name="Django for Beginners", description="Learn Django from scratch.", price=100)
        Course2.objects.create(name="Advanced Django", description="Deep dive into Django.", price=200)
    def test_course_list_view(self):
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'course_list.html')
        self.assertContains(response, "Django for Beginners")
        self.assertContains(response, "Advanced Django")
        print(response.content.decode())

class HelloTest(TestCase):
    def test_hello(self):
        client = TestClient(router)
        response = client.get("/hello")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"msg": "Hello World"})

class APITestCase(TestCase):
    base_url = '/api/v1/'
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher',
                                                password='password123')
        self.student = User.objects.create_user(username='student',
                                                password='password123')
        self.course = Course.objects.create(
            name="Django for Beginners",
            description="Learn Django from scratch.",
            price=100,
            teacher=self.teacher
        )
        login = self.client.post(self.base_url+'auth/sign-in',
                                 data=json.dumps({'username': 'teacher',
                                                  'password': 'password123'}),
                                 content_type='application/json')
        self.token = login.json()['access']
        login = self.client.post(self.base_url+'auth/sign-in',
                                 data=json.dumps({'username': 'student',
                                                  'password': 'password123'}),
                                 content_type='application/json')
        self.student_token = login.json()['access']
    def test_list_courses(self):
        response = self.client.get(f'{self.base_url}courses')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['items']), 1)
    def test_create_course(self):
        response = self.client.post(self.base_url+'courses', data={
            'name': 'New Course',
            'description': 'New Course Description',
            'price': 150,
            'file': {'image': None}
        }, format='multipart', **{'HTTP_AUTHORIZATION': 'Bearer ' +
                                                        str(self.token)})
        # print(response.request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'New Course')
    def test_update_course(self):
        response = self.client.post(f'{self.base_url}courses/{self.course.id}',
                                    data={
                                        'name': 'Updated Course',
                                        'description': 'Updated Description',
                                        'price': 200,
                                        'file': {'image': None}
                                    }, format='multipart', **{'HTTP_AUTHORIZATION': 'Bearer ' +
                                                                                    str(self.token)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Updated Course')
    def test_enroll_course(self):
        response = self.client.post(f'{self.base_url}courses/{self.course.id}/enroll',
                         **{'HTTP_AUTHORIZATION': 'Bearer ' + str(self.student_token)})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CourseMember.objects.filter(course_id=self.course,
                                                    user_id=self.student).exists())
    def test_create_content_comment(self):
        content = CourseContent.objects.create(course_id=self.course, name="Content Title", escription="ContentDescription")
        self.client.post(f'{self.base_url}courses/{self.course.id}/enroll',
                         **{'HTTP_AUTHORIZATION': 'Bearer ' +
                                                  str(self.student_token)})
        response = self.client.post(f'{self.base_url}contents/{content.id}/comments',
                         data={'comment': 'This is a comment'},
                         content_type='application/json',
                         **{'HTTP_AUTHORIZATION': 'Bearer ' + str(self.student_token)})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['comment'], 'This is a comment')
    def test_delete_comment(self):
        content = CourseContent.objects.create(course_id=self.course, name="Content Title", description="Content Description")
        self.client.post(f'{self.base_url}courses/{self.course.id}/enroll',
                         **{'HTTP_AUTHORIZATION': 'Bearer ' + str(self.student_token)})
        response = self.client.post(f'{self.base_url}contents/{content.id}/comments',
                         data={'comment': 'This is a comment'},
                         content_type='application/json',
                         **{'HTTP_AUTHORIZATION': 'Bearer ' + str(self.student_token)})
        comment_id = response.json()['id']
        response = self.client.delete(f'{self.base_url}comments/{comment_id}',
                                      **{'HTTP_AUTHORIZATION': 'Bearer ' +
                                                               str(self.student_token)})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Comment.objects.filter(id=comment_id).exists())
