PYTHON ?= python3
ROUND ?=
FILE ?=
SLICE ?=
CODE ?=
MEMBERS ?=
SELF ?=
STEP ?=
IOU ?=
TASK_ID ?=

.DEFAULT_GOAL := help
.PHONY: help doctor mode cvat draft parking lock reference compare local-quality cvat-quality model iou-sweep qa fill selfqc triage rework card degrade status check worked cleanup reset-task

help:
	@echo "Day 11 SVM/360 fisheye lab — lệnh học viên"
	@echo "  make doctor | make mode MEMBERS=ten [SELF=ten nếu nhóm] | make status"
	@echo "  make cvat SLICE=B1-edge [SUPPORT=1]"
	@echo "  make draft FILE=exports/ban-nhap.zip | make selfqc ROUND=r1_craft | make fill"
	@echo "  make parking [FILE=exports/parking.zip]"
	@echo "  make lock ROUND=r1_craft FILE=exports/r1.zip [RELOCK=1]"
	@echo "  make reference ROUND=r1_craft | make compare ROUND=r1_craft"
	@echo "  make local-quality | make model | make iou-sweep IOU=0.3,0.5,0.7"
	@echo "  make cvat-quality [TASK_ID=N] (tùy chọn nếu có CVAT Premium)"
	@echo "  make qa SLICE=B1-edge FILE=annotations.xml CODE=XXXX-XXXX"
	@echo "  make fill ROUND=r1_craft | make selfqc ROUND=r1_craft | make triage"
	@echo "  make rework | make card | make degrade STEP=k12 | make check"
	@echo "  make worked | make cleanup [YES=1] | make reset-task"

doctor:
	$(PYTHON) lab11.py doctor

mode:
	@test -n "$(MEMBERS)" || { echo "✗ Thiếu MEMBERS — ví dụ solo: make mode MEMBERS=an; nhóm: make mode MEMBERS=an,binh,chi SELF=binh" >&2; exit 2; }
	$(PYTHON) lab11.py mode --members "$(MEMBERS)" $(if $(SELF),--self "$(SELF)",)

cvat:
	@test -n "$(SLICE)" || { echo "✗ Thiếu SLICE — ví dụ: make cvat SLICE=B1-edge" >&2; exit 2; }
	$(PYTHON) lab11.py cvat "$(SLICE)" $(if $(filter 1,$(SUPPORT)),--support,)

draft:
	@test -n "$(FILE)" || { echo "✗ Thiếu FILE — ví dụ: make draft FILE=exports/ban-nhap.zip" >&2; exit 2; }
	$(PYTHON) lab11.py draft "$(FILE)"

parking:
	$(PYTHON) lab11.py parking $(if $(FILE),--file "$(FILE)",)

lock:
	@test -n "$(ROUND)" || { echo "✗ Thiếu ROUND — ví dụ: make lock ROUND=r1_craft FILE=exports/r1.zip" >&2; exit 2; }
	@test -n "$(FILE)" || { echo "✗ Thiếu FILE — ví dụ: make lock ROUND=r1_craft FILE=exports/r1.zip" >&2; exit 2; }
	$(PYTHON) lab11.py lock "$(ROUND)" "$(FILE)" $(if $(filter 1,$(RELOCK)),--relock,)

reference:
	@test -n "$(ROUND)" || { echo "✗ Thiếu ROUND — ví dụ: make reference ROUND=r1_craft" >&2; exit 2; }
	$(PYTHON) lab11.py reference "$(ROUND)"

compare:
	@test -n "$(ROUND)" || { echo "✗ Thiếu ROUND — ví dụ: make compare ROUND=r1_craft" >&2; exit 2; }
	$(PYTHON) lab11.py compare "$(ROUND)"

cvat-quality:
	$(PYTHON) lab11.py cvat-quality $(if $(TASK_ID),--task-id $(TASK_ID),)

local-quality:
	$(PYTHON) lab11.py local-quality

model:
	$(PYTHON) lab11.py model

iou-sweep:
	@test -n "$(IOU)" || { echo "✗ Thiếu IOU — ví dụ: make iou-sweep IOU=0.3,0.5,0.7" >&2; exit 2; }
	$(PYTHON) lab11.py iou-sweep --iou "$(IOU)"

qa:
	@test -n "$(SLICE)" || { echo "✗ Thiếu SLICE — ví dụ: make qa SLICE=B1-edge FILE=annotations.xml CODE=XXXX-XXXX" >&2; exit 2; }
	@test -n "$(FILE)" || { echo "✗ Thiếu FILE — ví dụ: make qa SLICE=B1-edge FILE=annotations.xml CODE=XXXX-XXXX" >&2; exit 2; }
	@test -n "$(CODE)" || { echo "✗ Thiếu CODE — ví dụ: make qa SLICE=B1-edge FILE=annotations.xml CODE=XXXX-XXXX" >&2; exit 2; }
	$(PYTHON) lab11.py qa --slice "$(SLICE)" --file "$(FILE)" --code "$(CODE)"

fill:
	$(PYTHON) lab11.py fill $(if $(ROUND),$(ROUND),r1_craft)

selfqc:
	@test -n "$(ROUND)" || { echo "✗ Thiếu ROUND — ví dụ: make selfqc ROUND=r1_craft" >&2; exit 2; }
	$(PYTHON) lab11.py selfqc "$(ROUND)"

triage:
	$(PYTHON) lab11.py triage

rework:
	$(PYTHON) lab11.py rework

card:
	$(PYTHON) lab11.py card

degrade:
	@test -n "$(STEP)" || { echo "✗ Thiếu STEP — ví dụ: make degrade STEP=k12" >&2; exit 2; }
	$(PYTHON) lab11.py degrade "$(STEP)"

status:
	$(PYTHON) lab11.py status

check:
	$(PYTHON) lab11.py check

worked:
	$(PYTHON) lab11.py worked

cleanup:
	$(PYTHON) lab11.py cleanup $(if $(filter 1,$(YES)),--yes,)

reset-task:
	$(PYTHON) lab11.py reset-task
