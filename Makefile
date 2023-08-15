VERSION := $(shell cat VERSION)

package-helm:
	helm package packaging/helm/helm-chart/

package-stx:
	cd packaging; tar -czvf ../poc-starlingx-stx-pkg.tar.gz *; cd -


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


package-fluxcd:
	echo 'TODO'
