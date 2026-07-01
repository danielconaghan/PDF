#
# veraPDF CLI — sourced from:
# https://github.com/veraPDF/veraPDF-apps/blob/integration/Dockerfile
#
FROM eclipse-temurin:21-jdk-alpine AS app-installer
ARG VERAPDF_VERSION
ARG VERAPDF_MINOR_VERSION
ARG VERAPDF_INSTALLER_FOLDER
ENV VERAPDF_VERSION=${VERAPDF_VERSION:-1.30}
ENV VERAPDF_MINOR_VERSION=${VERAPDF_MINOR_VERSION:-2}
ENV VERAPDF_INSTALLER_FOLDER=${VERAPDF_INSTALLER_FOLDER:-releases}

WORKDIR /tmp
COPY docker-install.xml .
RUN wget -O /tmp/verapdf-installer.zip https://software.verapdf.org/${VERAPDF_INSTALLER_FOLDER}/${VERAPDF_VERSION}/verapdf-greenfield-${VERAPDF_VERSION}.${VERAPDF_MINOR_VERSION}-installer.zip
RUN unzip verapdf-installer.zip && java -jar ./verapdf-greenfield-${VERAPDF_VERSION}.${VERAPDF_MINOR_VERSION}/verapdf-izpack-installer-${VERAPDF_VERSION}.${VERAPDF_MINOR_VERSION}.jar docker-install.xml

FROM eclipse-temurin:21-jdk-alpine AS jre-builder
RUN "$JAVA_HOME/bin/jlink" \
         --add-modules java.base,java.compiler,java.logging,java.xml,jdk.crypto.ec,java.desktop,jdk.management \
         --strip-debug \
         --no-man-pages \
         --no-header-files \
         --compress=2 \
         --output /javaruntime

FROM alpine:3

ARG JAVA_OPTS
ENV JAVA_OPTS=$JAVA_OPTS
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"
COPY --from=jre-builder /javaruntime $JAVA_HOME

RUN addgroup -S verapdf && adduser -S -G verapdf -h /opt/verapdf verapdf
RUN mkdir --parents /var/opt/verapdf/logs && chown -R verapdf:verapdf /var/opt/verapdf

USER verapdf
COPY --from=app-installer /opt/verapdf/ /opt/verapdf/

WORKDIR /data
VOLUME /data

ENTRYPOINT ["/opt/verapdf/verapdf"]
