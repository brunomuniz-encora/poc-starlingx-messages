#####################################################################################################################
### StarlingX App packaging. ########################################################################################
### This section is an implementation of what's specified in the BuildGuide. ########################################
### See https://github.com/bmuniz-daitan/poc-starlingx-messages/blob/main/BuildGuide.md#packaging-the-application ###
#####################################################################################################################

CHART_NAME := $(shell cat helm-chart/Chart.yaml | grep name | awk -F ': ' '{print $$2}')
CHART_VERSION := $(shell cat helm-chart/Chart.yaml | grep -E '^version' | awk -F ': ' '{print $$2}')

package-helm:
	helm package helm-chart/

package-plugin:
	cd stx-plugin; \
	python3 setup.py bdist_wheel \
	--universal -d k8sapp_poc_starlingx
	# clean up
	rm -r stx-plugin/build/ stx-plugin/k8sapp_poc_starlingx.egg-info/ stx-plugin/AUTHORS stx-plugin/ChangeLog

package-stx: package-helm package-plugin
	mkdir -p stx-packaging/charts
	mkdir -p stx-packaging/plugins
	mv poc-starlingx*.tgz stx-packaging/charts/
	mv stx-plugin/k8sapp_poc_starlingx/k8sapp_poc_starlingx*.whl stx-packaging/plugins/
	cd stx-packaging; find . -type f ! -name '*.sha256' -print0 | xargs -0 sha256sum > ../poc-starlingx-stx-pkg.tar.gz.sha256
	cd stx-packaging; tar -czvf ../poc-starlingx-stx-pkg.tar.gz *
	# clean up
	rm -r stx-packaging/charts/
	rm -r stx-packaging/plugins/

#################################
######## Debian packaging #######
#### (this is just a helper) ####
#################################

TEMP_DIR := $(shell mktemp -d)
DEBIAN_DIR = $(TEMP_DIR)/DEBIAN
DEBIAN_control = $(DEBIAN_DIR)/control
DEBIAN_postinst = $(DEBIAN_DIR)/postinst
DEBIAN_postrm = $(DEBIAN_DIR)/postrm
DEBIAN_prerm = $(DEBIAN_DIR)/prerm
USR_DIR = $(TEMP_DIR)/usr
PKG_DIR = $(TEMP_DIR)/usr/share/poc-starlingx

debian-create-dirs:
	mkdir $(DEBIAN_DIR) $(USR_DIR)
	mkdir -p $(PKG_DIR)

debian-copy-files: debian-create-dirs
	find ./src -type d -name "__pycache__" -exec rm -r {} +
	find ./src -type f -exec cp -t $(PKG_DIR) {} +
	cp requirements/requirements.txt $(PKG_DIR)

debian-create-scripts: debian-copy-files
	touch $(DEBIAN_control)
	chmod 644 $(DEBIAN_control)
	touch $(DEBIAN_postinst)
	chmod +x $(DEBIAN_postinst)
	touch $(DEBIAN_postrm)
	chmod +x $(DEBIAN_postrm)
	touch $(DEBIAN_prerm)
	chmod +x $(DEBIAN_prerm)

debian-write-control: debian-create-scripts
	echo 'Package: poc-starlingx' > $(DEBIAN_control)
	echo 'Version: $(VERSION)' >> $(DEBIAN_control)
	echo 'Architecture: all' >> $(DEBIAN_control)
	echo 'Maintainer: Bruno Muniz <bruno.muniz@encora.com>' >> $(DEBIAN_control)
	echo 'Description: A simple app that exchanges HTTP messages and generates demo data.' >> $(DEBIAN_control)

debian-write-postinst: debian-write-control
	echo '#!/bin/sh' > $(DEBIAN_postinst)
	echo 'export MODE=central' >> $(DEBIAN_postinst)
	echo 'mkdir -p /opt/poc-starlingx/venv' >> $(DEBIAN_postinst)
	echo 'python3 -m venv /opt/poc-starlingx/venv' >> $(DEBIAN_postinst)
	echo '. /opt/poc-starlingx/venv/bin/activate' >> $(DEBIAN_postinst)
	echo 'pip install -r /usr/share/poc-starlingx/requirements.txt' >> $(DEBIAN_postinst)
	echo 'touch /var/log/poc-starlingx.log' >> $(DEBIAN_postinst)
	echo 'nohup /usr/share/poc-starlingx/main.py > /var/log/poc-starlingx.log 2>&1 &' >> $(DEBIAN_postinst)
	echo 'echo "The poc-startlingx application has been started."' >> $(DEBIAN_postinst)

debian-write-prerm: debian-write-postinst
	echo 'pkill -f "/usr/share/poc-starlingx/main.py"' > $(DEBIAN_prerm)
	echo 'sleep 2' >> $(DEBIAN_prerm)
	echo 'rm -rf /opt/poc-starlingx/venv' >> $(DEBIAN_prerm)
	echo 'rm -f /var/log/poc-starlingx.log' >> $(DEBIAN_prerm)
	echo 'echo "The poc-starlingx application has been stopped."' >> $(DEBIAN_prerm)

package-debian: debian-write-prerm
	dpkg-deb --build $(TEMP_DIR) .
	echo 'You can now install the package with "sudo dpkg -i <.deb file>".'

#################################
### Docker packaging of ./src ###
#### (this is just a helper) ####
#################################

VERSION := $(shell cat VERSION)

docker-build:
	echo "Attention, this is just a helper, it expects 'brunomuniz' to be logged in"
	echo "We might automate this, if necessary, in the future"
	echo "Alright? (yes)"
	read y
	docker build -t brunomuniz/poc-starlingx:$(VERSION) .

docker-push-latest: docker-build
	docker tag brunomuniz/poc-starlingx:$(VERSION) brunomuniz/poc-starlingx:latest
	docker push brunomuniz/poc-starlingx:$(VERSION)
	docker push brunomuniz/poc-starlingx:latest
