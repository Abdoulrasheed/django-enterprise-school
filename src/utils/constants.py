from django.utils.translation import ugettext_lazy as _


FIRST = "First"
SECOND = "Second"
THIRD = "Third"
TERM = (
	(FIRST, _("First")),
	(SECOND, _("Second")),
	(THIRD, _("Third")),
)

OPTIONAL = "Optional"
MANDATORY = "Mandatory"
SUBJECT_TYPE = (
  (OPTIONAL, _("Optional")),
  (MANDATORY, _("Mandatory")),
)


MR = "Mr."
MS = "Ms."
MRS = "Mrs."
MISS = "Miss"
MALAM = "Malam"
MADAM = "Madam"
PROF = "Prof."
ALHAJI = "Alhaji"
TITLES = (
  (MR, _("Mr.")),
  (MS, _("Ms")),
  (MRS, _("Mrs")),
  (MISS, _("Miss")),
  (MALAM, _("Malam")),
  (MADAM, _("Madam")),
  (PROF, _("Prof.")),
  (ALHAJI, _("Alhaji")),
)


BROTHER = "Brother"
SISTER = "Sister"
DAUGTHER = "Daughter"
SON = "Son"
FATHER = "Father"
MOTHER = "Mother"

NOK_RELATIONSHIPS = (
  (BROTHER, _("Brother")),
  (SISTER, _("Sister")),
  (DAUGTHER, _("Daughter")),
  (SON, _("Son")),
  (FATHER, _("Father")),
  (MOTHER, _("Mother")),
  )

MSG_FROM = "BaYola"

CASH = "Cash"
CHEAQUE = "Cheaque"

PAYMENT_METHOD = (
	(CASH, _("Cash")),
	(CHEAQUE, _("Cheaque")),
)

PAID = "Paid"
NOT_PAID = "Not Paid"
PARTIALLY_PAID = "Partially Paid"

PAYMENT_STATUS = (
	(PAID, _("Fully Paid")),
	(NOT_PAID, _("Not Paid")),
	(PARTIALLY_PAID, _("Partially Paid")),
)

MALE = "Male"
FMALE = "Female"

GENDER = (
	(MALE, _("Male")),
	(FMALE, _("Female"))
	)

ISLAM = "Islam"
CHRISTIANITY = "Christianity"

RELIGION = (
	(ISLAM, _("Islam")),
	(CHRISTIANITY, _("Christianity")),
	)

STATE = (
  ("", "Choose"),
  ("Abia", "Abia"),
  ("Adamawa", "Adamawa"),
  ("Anambra", "Anambra"),
  ("Akwa Ibom", "Akwa Ibom"),
  ("Bauchi", "Bauchi"),
  ("Bayelsa", "Bayelsa"),
  ("Benue", "Benue"),
  ("Borno", "Borno"),
  ("Cross River", "Cross River"),
  ("Delta", "Delta"),
  ("Ebonyi", "Ebonyi"),
  ("Enugu", "Enugu"),
  ("Edo", "Edo"),
  ("Ekiti", "Ekiti"),
  ("FCT - Abuja", "FCT - Abuja"),
  ("Gombe", "Gombe"),
  ("Imo", "Imo"),
  ("Jigawa", "Jigawa"),
  ("Kaduna", "Kaduna"),
  ("Kano", "Kano"),
  ("Katsina", "Katsina"),
  ("Kebbi", "Kebbi"),
  ("Kogi", "Kogi"),
  ("Kwara", "Kwara"),
  ("Lagos", "Lagos"),
  ("Nasarawa", "Nasarawa"),
  ("Niger", "Niger"),
  ("Ogun", "Ogun"),
  ("Ondo", "Ondo"),
  ("Osun", "Osun"),
  ("Oyo", "Oyo"),
  ("Plateau", "Plateau"),
  ("Rivers", "Rivers"),
  ("Sokoto", "Sokoto"),
  ("Taraba", "Taraba"),
  ("Yobe", "Yobe"),
  ("Zamfara", "Zamfara"),
)

LGA = (
	("Yola North", "Yola North"),
	("Yola South", "Yola South"),
	)

A = "A"
B = "B"
C = "C"
D = "D"
E = "E"
F = "F"

GRADE = (
		(A, 'A'),
		(B, 'B'),
		(C, 'C'),
		(D, 'D'),
		(E, 'E'),
		(F, 'F'),
	)


SUCCESS = "Success"
ERROR = "Error"
INFO = "Info"
NOTIFICATION_TYPE = (
	(SUCCESS, _("Success")),
	(ERROR, _("Error")),
	(INFO, _("Info")),
	)

DRAFT = "D"
DELIVERED = "S"
PENDING = "P"

STATUS = (
    (DRAFT, _("Draft")),
    (DELIVERED, _("Delivered")),
    (PENDING, _("Pending")),
)