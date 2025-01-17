########################################################################
#
# $Id: package.spec.in 12090 2009-05-16 22:28:39Z marcusmeissner $
#
# RPM spec file for libgphoto2
#
# TODO list concerning packaging
# - review and coordinate RPM packaging for libgphoto2, gphoto2, gtkam
#
########################################################################

%define debug_package %{nil}

####################################
Summary: Software for accessing digital cameras
Name: libgphoto2
Version: 2.5.8
Release: 2
License: LGPL
Group: Applications/Multimedia
BuildRoot: %{_tmppath}/%{name}-%{version}-root
# sources only available from sf.net - but not wgettable.
# Source: http://www.gphoto.org/dist/libgphoto2-2.5.8.tar.gz
Source: http://prdownloads.sourceforge.net/gphoto/libgphoto2-2.5.8.tar.gz
Url: http://www.gphoto.org/
ExcludeArch: s390 s390x
Provides: libgphoto2
Provides: libgphoto2_port
Requires: libgphoto2_port
# absolute requirements
PreReq: hotplug >= 2001_04_24-13
PreReq: /sbin/ldconfig, grep, fileutils
BuildRequires: findutils perl

# the following requirements are optional
#BuildRequires: gtk-doc
Requires: libusb >= 0.1.8
BuildRequires: libusb-devel >= 0.1.8

####################################
%description
The gPhoto2 project is a universal, free application and library
framework that lets you download images from several different
digital camera models, including the newer models with USB
connections. Note that
a) for some older camera models you must use the old "gphoto" package.
b) for USB mass storage models you must use the driver in the kernel

This libgphoto2 package contains only the library that digital 
camera applications can use.

Frontend like the command-line utility gphoto2 and other (GUI)
frontends are available seperately.

####################################
%package devel
Summary: Headers and libraries to compile against the libgphoto2 library.
Requires: %{name} = %{version}
Provides: libgphoto2-devel
Provides: libgphoto2_port-devel
Group: Development/Libraries

####################################
%description devel
The gPhoto2 project is a universal, free application and library
framework that lets you download images from several different
digital camera models, including the newer models with USB
connections. Note that
a) for some older camera models you must use the old "gphoto" package.
b) for USB mass storage models you must use the driver in the kernel

This libgphoto2-devel package contains the files needed to compile 
frontends like the command-line utility gphoto2 and other (GUI)
frontends, which are available seperately.


########################################################################
# Building and installing the beast into %{buildroot}
########################################################################

####################################
%prep
rm -rf "${RPM_BUILD_DIR}/%{name}-%{version}"
%setup -q -n %{name}-%{version}

####################################
%build
%define __libtoolize :
# FIXME: We should copy the disable- arguments here
##FIXMEPERCENTconfigure --enable-docs --with-docs-dir=%{buildroot}%{_docdir}/%{name}
%configure --with-docs-dir=%{buildroot}%{_docdir}/%{name}
make

####################################
%install
rm -rf "${RPM_BUILD_ROOT}"

# Convince gphoto2 to be packaged.
perl -p -i -e "s|^libdir.*|libdir='$RPM_BUILD_ROOT%{_libdir}'|g" \
	libgphoto2_port/libgphoto2_port/libgphoto2_port.la

%makeinstall

# Fix up libtool libraries.
find $RPM_BUILD_ROOT -name '*.la' | \
  xargs perl -p -i -e "s|$RPM_BUILD_ROOT||g"

#cp -a %{buildroot}%{_docdir}/%{name}-%{version}/html html
#cp -a %{buildroot}%{_docdir}/libgphoto2_port-0.5.1/html/api/gphoto2-port html/api
#find html -name '*.sgml' | xargs rm


%find_lang libgphoto2-6
# FIXME: Update this manually as long as libgphoto2_port has a
#        different build system.
%find_lang libgphoto2_port-0

# build file list
find %{buildroot} -type f -or -type l \
        | sed 's!^%{buildroot}!!' | sort > %{name}-%{version}.all.files

# extract .so libs
egrep '\.so(\.[0-9]+)*$' \
	< %{name}-%{version}.all.files > %{name}-%{version}.so.files
egrep -v '\.so(\.[0-9]+)*$' \
	< %{name}-%{version}.all.files > %{name}-%{version}.no-so.files

# extract files for devel package
egrep '(-config|\.h|\.la|\.a|\.pc|\.3)$' \
	< %{name}-%{version}.no-so.files > %{name}-%{version}.devel.files
egrep -v '(-config|\.h|\.la|\.a|\.pc|\.3)$' \
	< %{name}-%{version}.no-so.files > %{name}-%{version}.no-devel.files

# extract doc files
egrep '^%{_docdir}' \
	< %{name}-%{version}.no-devel.files > %{name}-%{version}.doc.files
egrep -v '^%{_docdir}' \
	< %{name}-%{version}.no-devel.files > %{name}-%{version}.no-doc.files

# extract i18n files
egrep '^%{_datadir}/locale' \
	< %{name}-%{version}.no-doc.files > %{name}-%{version}.i18n.files
egrep -v '^%{_datadir}/locale' \
	< %{name}-%{version}.no-doc.files > %{name}-%{version}.no-i18n.files

# extract misc files for lib package
egrep '^(%{_libdir}|%{_datadir})/libgphoto2' \
	< %{name}-%{version}.no-i18n.files > %{name}-%{version}.misc.files
egrep -v '^(%{_libdir}|%{_datadir})/libgphoto2' \
	< %{name}-%{version}.no-i18n.files > %{name}-%{version}.rest.files \
	|| echo "non-zero exit code is not fatal here"

if [ -s %{name}-%{version}.rest.files ]
then
	cat %{name}-%{version}.rest.files
fi

cat %{name}-%{version}.{so,doc,misc,i18n}.files \
	> %{name}-%{version}.files

# HACK
touch debugfiles.list

exit 0

####################################
%clean
# FIXME: Cleanup deactiveated for debugging
# rm -rf "${RPM_BUILD_ROOT}"

########################################################################
# file list and installation for main package
########################################################################

####################################
%files -f %{name}-%{version}.files
%defattr(-,root,root)
# FIXME: correct %docxyz markup for doc files

####################################
%post

# register libraries
/sbin/ldconfig

# add supported cameras to /etc/hotplug/usb.usermap
grep -v '^usbcam' /etc/hotplug/usb.usermap > /etc/hotplug/usb.usermap.tmp
%{_libdir}/libgphoto2/print-usb-usermap >> /etc/hotplug/usb.usermap.tmp
mv /etc/hotplug/usb.usermap.tmp /etc/hotplug/usb.usermap

####################################
%postun

# unregister libraries
/sbin/ldconfig

if [ "$1" = 0 ]; then
    # remove supported cameras from /etc/hotplug/usb.usermap
    # if erasing the package not as part of a package update
    grep -v '^usbcam' /etc/hotplug/usb.usermap > /etc/hotplug/usb.usermap.new
    mv /etc/hotplug/usb.usermap.new /etc/hotplug/usb.usermap
fi


########################################################################
# file list and installation for -devel subpackage
########################################################################

####################################
%files devel -f %{name}-%{version}.devel.files
%defattr(-,root,root)
#%doc html/api


########################################################################
# ChangeLog
########################################################################
%changelog
* Thu Jun 20 2002 Hans Ulrich Niedermann <gp@n-dimensional.de> 2.1.4head
- hack in correct find_lang arguments
- fix misc. nagging little things preventing "rpmbuild -ta" from working

* Thu Jun 20 2002 Hans Ulrich Niedermann <gp@n-dimensional.de> 2.1.0rc3-1
- only --enable-docs and copy API docs if GTK_DOC found
- use --with-doc-formats from local ./configure call

* Tue May 28 2002 Hans Ulrich Niedermann <gp@n-dimensional.de> 2.0.1dev8-1
- comment out requirements if not used (gtk-doc, transfig)
- provide libgphoto2_port - for future compatibility
- fixed handling of misc HTML docs (API docs and docbook-generated manual)
- install linux-hotplug scripts into a directory of that name
- added gphoto2_port(3) man page

* Sat May 18 2002 Hans Ulrich Niedermann <gp@n-dimensional.de> 2.0.1dev6-1
- added API HTML docs to the -devel package
- added man page gphoto2(3), require hotplug >= 2001_04_24-13

* Thu May  9 2002 Hans Ulrich Niedermann <gp@n-dimensional.de> 2.0.1dev4-1
- merged changes from current Redhat spec file into gphoto2 distribution
  as they managed to get the beast to build
- re-added FAQ to package (Redhat left it out regrettably)
- only require hotplug 2001_04_24-11 instead of 2001_04_24-13

* Mon Apr 29 2002 Tim Waugh <twaugh@redhat.com> 2.0-6
- In fact, don't even build for mainframe.

* Mon Apr 29 2002 Florian La Roche <Florian.LaRoche@redhat.de> 2.0-5
- do not require hotplug for mainframe

* Mon Apr 15 2002 Nalin Dahyabhai <nalin@redhat.com> 2.0-4
- Set the owner of the device to the console lock holder, not the owner
  of /dev/console, in the hotplug agent, fixing access for users who log
  in at VTs and use startx (#62976).

* Fri Apr 12 2002 Tim Waugh <twaugh@redhat.com> 2.0-3
- Rebuild (fixed bug #63355).

* Sat Apr 06 2002 Hans Ulrich Niedermann <gp@n-dimensional.de>
- require libusb >= 0.0.5 and for building require transfig

* Wed Feb 27 2002 Tim Waugh <twaugh@redhat.com> 2.0-2
- Fix from CVS: close port unconditionally in gp_camera_exit().

* Mon Feb 25 2002 Tim Waugh <twaugh@redhat.com> 2.0-1
- 2.0 is released.
- Ship the .so symlinks in the devel package.

* Mon Feb 25 2002 Tim Waugh <twaugh@redhat.com> 2.0-0.rc4.1
- 2.0rc4.

* Fri Feb 22 2002 Tim Waugh <twaugh@redhat.com> 2.0-0.rc3.1
- 2.0rc3.  No longer need CVS patch.
- Build no longer requires xmlto.

* Thu Feb 21 2002 Tim Waugh <twaugh@redhat.com> 2.0-0.rc2.2
- Fix DC240 hangs (patch from CVS).
- Rebuild in new environment.

* Tue Feb 19 2002 Tim Waugh <twaugh@redhat.com> 2.0-0.rc2.1
- 2.0rc2 (bug #59993).  No longer need docs patch or man page.
- Really fix up libtool libraries (bug #60002).

* Fri Feb 15 2002 Tim Waugh <twaugh@redhat.com> 2.0-0.beta5.2
- PreReq /sbin/ldconfig, grep, and fileutils (bug #59941).

* Tue Feb 12 2002 Tim Waugh <twaugh@redhat.com> 2.0-0.beta5.1
- 2.0beta5.
- Fix Makefiles so that documentation can be built.
- Ship pkgconfig file.
- Add man page.

* Thu Feb  7 2002 Tim Waugh <twaugh@redhat.com> 2.0-0.beta4.1
- 2.0beta4.
- Build requires transfig, and at least version 0.1.5 of libusb.
- Clean up file lists.
- Build documentation.

* Fri Jan 25 2002 Tim Waugh <twaugh@redhat.com> 2.0-0.beta3.2
- Rebuild in new environment.
- Dump docbook-dtd30-sgml requirement; gtk-doc is sufficient.

* Sun Nov 18 2001 Tim Waugh <twaugh@redhat.com> 2.0-0.beta3.1
- Adapted for Red Hat Linux.

* Sat Oct 27 2001 Hans Ulrich Niedermann <gp@n-dimensional.de>
- fixed update behaviour for hotplug list (do not erase it when updating)

* Thu Oct 25 2001 Tim Waugh <twaugh@redhat.com>
- hotplug dependency is a prereq not a requires (the package scripts
  need it)

* Sun Oct 14 2001 Hans Ulrich Niedermann <gp@n-dimensional.de>
- integrated spec file into source package

* Sun Oct 14 2001 Hans Ulrich Niedermann <gp@n-dimensional.de>
- 2.0beta3

* Tue Oct  2 2001 Tim Waugh <twaugh@redhat.com> 2.0beta2-0.1
- Adapted for Red Hat Linux.
- 2.0beta2.

* Mon Aug  6 2001 Till Kamppeter <till@mandrakesoft.com> 2.0-0.beta1.2mdk
- Corrected "Requires:"

* Mon Aug  6 2001 Till Kamppeter <till@mandrakesoft.com> 2.0-0.beta1.1mdk
- Initial release



########################################################################
# Local Variables:
# mode: rpm-spec
# End:
