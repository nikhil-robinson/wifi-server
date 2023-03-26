#!/bin/bash

VERSION=0.6.7
PROGNAME="$(basename $0)"

export LC_ALL=C

SCRIPT_UMASK=0122
umask $SCRIPT_UMASK

phead() {
    echo "linux-router $VERSION (https://github.com/garywill/linux-router)"
}
phead2() {
    echo "Released under LGPL, with no warranty. Use on your own risk."
}
usage() {
    phead
    phead2
    cat << EOF

Usage: $PROGNAME <options>

Options:
    -h, --help              Show this help
    --version               Print version number

    -i <interface>          Interface to make NATed sub-network,
                            and to provide Internet to
                            (To create WiFi hotspot use '--ap' instead)
    -o <interface>          Specify an inteface to provide Internet from.
                            (See Notice 1)
                            (Note using this with default DNS option may leak
                            queries to other interfaces)
    -n                      Do not provide Internet (See Notice 1)
    --ban-priv              Disallow clients to access my private network
    
    -g <ip>                 This host's IPv4 address in subnet (mask is /24)
                            (example: '192.168.5.1' or '5' shortly)
    -6                      Enable IPv6 (NAT)
    --no4                   Disable IPv4 Internet (not forwarding IPv4)
                            (See Notice 1). Usually used with '-6'
                            
    --p6 <prefix>           Set IPv6 LAN address prefix (length 64) 
                            (example: 'fd00:0:0:5::' or '5' shortly) 
                            Using this enables '-6'
                            
    --dns <ip>|<port>|<ip:port>
                            DNS server's upstream DNS.
                            Use ',' to seperate multiple servers
                            (default: use /etc/resolve.conf)
                            (Note IPv6 addresses need '[]' around)
    --no-dns                Do not serve DNS
    --no-dnsmasq            Disable dnsmasq server (DHCP, DNS, RA)
    --catch-dns             Transparent DNS proxy, redirect packets(TCP/UDP) 
                            whose destination port is 53 to this host
    --log-dns               Show DNS query log (dnsmasq)
    --dhcp-dns <IP1[,IP2]>|no
                            Set IPv4 DNS offered by DHCP (default: this host).
    --dhcp-dns6 <IP1[,IP2]>|no
                            Set IPv6 DNS offered by DHCP (RA) 
                            (default: this host)
                            (Note IPv6 addresses need '[]' around)
                            Using both above two will enable '--no-dns' 
    --hostname <name>       DNS server associate this name with this host.
                            Use '-' to read name from /etc/hostname
    -d                      DNS server will take into account /etc/hosts
    -e <hosts_file>         DNS server will take into account additional 
                            hosts file
    --dns-nocache           DNS server no cache
    
    --mac <MAC>             Set MAC address
    --random-mac            Use random MAC address
 
    --tp <port>             Transparent proxy,
                            redirect non-LAN TCP and UDP(not tested) traffic to
                            port. (usually used with '--dns')
    
  WiFi hotspot options:
    --ap <wifi interface> <SSID>
                            Create WiFi access point
    -p, --password <password>   
                            WiFi password
    --qr                    Show WiFi QR code in terminal (need qrencode)
    
    --hidden                Hide access point (not broadcast SSID)
    --no-virt               Do not create virtual interface
                            Using this you can't use same wlan interface
                            for both Internet and AP
    --virt-name <name>      Set name of virtual interface
    -c <channel>            Channel number (default: 1)
    --country <code>        Set two-letter country code for regularity
                            (example: US)
    --freq-band <GHz>       Set frequency band: 2.4 or 5 (default: 2.4)
    --driver                Choose your WiFi adapter driver (default: nl80211)
    -w <WPA version>        '2' for WPA2, '1' for WPA, '1+2' for both
                            (default: 2)
    --psk                   Use 64 hex digits pre-shared-key instead of
                            passphrase
    --mac-filter            Enable WiFi hotspot MAC address filtering
    --mac-filter-accept     Location of WiFi hotspot MAC address filter list
                            (defaults to /etc/hostapd/hostapd.accept)
    --hostapd-debug <level> 1 or 2. Passes -d or -dd to hostapd
    --isolate-clients       Disable wifi communication between clients
    
    --ieee80211n            Enable IEEE 802.11n (HT)
    --ieee80211ac           Enable IEEE 802.11ac (VHT)
    --ht_capab <HT>         HT capabilities (default: [HT40+])
    --vht_capab <VHT>       VHT capabilities
    
    --no-haveged            Do not run haveged automatically when needed

  Instance managing:
    --daemon                Run in background
    -l, --list-running      Show running instances
    --lc, --list-clients <id|interface>     
                            List clients of an instance. Or list neighbors of
                            an interface, even if it isn't handled by us.
                            (passive mode)
    --stop <id>             Stop a running instance
        For <id> you can use PID or subnet interface name.
        You can get them with '--list-running'

    Notice 1:   This script assume your host's default policy won't forward
                packets, so the script won't explictly ban forwarding in any
                mode. In some unexpected case (eg. mistaken configurations) may
                cause unwanted packets leakage between 2 networks, which you
                should be aware of if you want isolated network
                
Examples:
    $PROGNAME -i eth1
    $PROGNAME --ap wlan0 MyAccessPoint -p MyPassPhrase
    $PROGNAME -i eth1 --tp <transparent-proxy> --dns <dns-proxy>
EOF
}

check_empty_option(){
    if [[ "$1" == "" ]]; then
        usage
        exit 0
    fi
}


define_global_variables(){
    # user options
    GATEWAY=  # IPv4 address for this host
    PREFIX6=  # IPv6 LAN address prefix for this host
    IID6=1    # IPv6 LAN ID for this host
    IPV6=0  # enable ipv6
    NO4=0   # no IPv4 Internet
    BANLAN=0 # ban clients from accessing private addresses
    DHCP_DNS=gateway  # which ipv4 DNS the DHCP gives clients
    DHCP_DNS6=gateway # which ipv6 DNS the DHCP gives clients
    dnsmasq_NO_DNS=0  # disable dns server
    NO_DNSMASQ=0  # disable dnsmasq (dns and dhcp)
    CATCH_DNS=0   # catch clients 53 port packets
    SHOW_DNS_QUERY=0  # log dns
    ETC_HOSTS=0
    ADDN_HOSTS=
    DNS_NOCACHE=
    CONN_IFACE=    # which interface user choose to use to create network
    INTERNET_IFACE= # which interface to get Internet from
    THISHOSTNAME=   # this host's name the DNS tells clients 
    TP_PORT=  # transparent proxy port
    DNS=  # upstream DNS
    MAC_USE_RANDOM=0
    NEW_MACADDR=
    DAEMONIZE=0
    
    # script variables
    SUBNET_IFACE=  # which interface to create network
    SHARE_METHOD=nat 
    OLD_MACADDR=
    

    ##### wifi hotspot
    # user options
    HIDDEN=0 # hidden wifi hotspot
    WIFI_IFACE=
    CHANNEL=default 
    WPA_VERSION=2
    MAC_FILTER=0
    MAC_FILTER_ACCEPT=/etc/hostapd/hostapd.accept
    IEEE80211N=0
    IEEE80211AC=0
    HT_CAPAB='[HT40+]'
    VHT_CAPAB=
    DRIVER=nl80211
    NO_VIRT=0 # not use virtual interface
    COUNTRY=
    FREQ_BAND=2.4
    NO_HAVEGED=0
    HOSTAPD_DEBUG_ARGS=
    USE_PSK=0
    ISOLATE_CLIENTS=0
    QR=0 # show wifi qr
    
    # script variables
    VWIFI_IFACE=  # virtual wifi interface name, if created
    VIRT_NAME= # name to use for virtual interface if --virt-name is used
    AP_IFACE=     # can be VWIFI_IFACE or WIFI_IFACE
    USE_IWCONFIG=0  # some device can't use iw
    
    #######
    
    #-- to deal with info of a running instance. then will exit
    LIST_RUNNING=0
    STOP_ID=
    LIST_CLIENTS_ID=

    # -- variables for running
    CONFDIR=
    NM_RUNNING=0
    NM_UNM_LIST=  # it's called "list" but for now one interface
}

parse_user_options(){
    while [[ -n "$1" ]]; do
        case "$1" in
            -h|--help)
                usage
                exit 0
                ;;
            --version)
                echo "$VERSION"
                exit 0
                ;;
            -i)
                shift
                CONN_IFACE="$1"
                shift
                ;;
            -o)
                shift
                INTERNET_IFACE="$1"
                shift
                ;;
            -n)
                shift
                SHARE_METHOD=none
                ;;
            --ban-priv)
                shift
                BANLAN=1
                ;;
            --tp)
                shift
                TP_PORT="$1"
                SHARE_METHOD=redsocks
                shift
                ;;
                
                
            -g)
                shift
                GATEWAY="$1"
                shift
                ;;
            -6)
                shift
                IPV6=1
                ;;
            --no4)
                shift
                NO4=1
                ;;
            --p6)
                shift
                PREFIX6="$1"
                IPV6=1
                shift
                ;;
            --mac)
                shift
                NEW_MACADDR="$1"
                shift
                ;;
            --random-mac)
                shift
                MAC_USE_RANDOM=1
                ;;
                
            --dns)
                shift
                DNS="$1"
                shift
                ;;
            --no-dns)
                shift
                dnsmasq_NO_DNS=1
                ;;
            --no-dnsmasq)
                shift
                NO_DNSMASQ=1
                ;;
            --dhcp-dns)
                shift
                DHCP_DNS="$1"
                shift
                ;;
            --dhcp-dns6)
                shift
                DHCP_DNS6="$1"
                shift
                ;;
            --catch-dns)
                shift
                CATCH_DNS=1
                ;;    
            --log-dns)
                shift
                SHOW_DNS_QUERY=1
                ;;
            --hostname)
                shift
                THISHOSTNAME="$1"
                shift
                ;;
            -d)
                shift
                ETC_HOSTS=1
                ;;
            -e)
                shift
                ADDN_HOSTS="$1"
                shift
                ;;
            --dns-nocache)
                shift
                DNS_NOCACHE=1
                ;;
            
            --isolate-clients)
                shift
                ISOLATE_CLIENTS=1
                ;;
                
            --ap)
                shift
                WIFI_IFACE="$1"
                shift
                SSID="$1"
                shift
                ;;
            -p|--password)
                shift
                PASSPHRASE="$1"
                shift
                ;;
            --qr)
                shift
                QR=1
                ;;
                
                
            --hidden)
                shift
                HIDDEN=1
                ;;
            --mac-filter)
                shift
                MAC_FILTER=1
                ;;
            --mac-filter-accept)
                shift
                MAC_FILTER_ACCEPT="$1"
                shift
                ;;

            -c)
                shift
                CHANNEL="$1"
                shift
                ;;
            -w)
                shift
                WPA_VERSION="$1"
                [[ "$WPA_VERSION" == "2+1" ]] && WPA_VERSION=1+2
                shift
                ;;

            --ieee80211n)
                shift
                IEEE80211N=1
                ;;
            --ieee80211ac)
                shift
                IEEE80211AC=1
                ;;
            --ht_capab)
                shift
                HT_CAPAB="$1"
                shift
                ;;
            --vht_capab)
                shift
                VHT_CAPAB="$1"
                shift
                ;;
            --driver)
                shift
                DRIVER="$1"
                shift
                ;;
            --no-virt)
                shift
                NO_VIRT=1
                ;;
            --virt-name)
                shift
                VIRT_NAME="$1"
                shift
                ;;

            --country)
                shift
                COUNTRY="$1"
                shift
                ;;
            --freq-band)
                shift
                FREQ_BAND="$1"
                shift
                ;;
            --no-haveged)
                shift
                NO_HAVEGED=1
                ;;
            --hostapd-debug)
                shift
                if [ "x$1" = "x1" ]; then
                    HOSTAPD_DEBUG_ARGS="-d"
                elif [ "x$1" = "x2" ]; then
                    HOSTAPD_DEBUG_ARGS="-dd"
                else
                    printf "Error: argument for --hostapd-debug expected 1 or 2, got %s\n" "$1"
                    exit 1
                fi
                shift
                ;;
            --psk)
                shift
                USE_PSK=1
                ;;

            --daemon)
                shift
                DAEMONIZE=1
                ;;
            --stop)
                shift
                STOP_ID="$1"
                shift
                ;;
            -l|--list-running)
                shift
                LIST_RUNNING=1
                ;;
            --lc|--list-clients)
                shift
                LIST_CLIENTS_ID="$1"
                shift
                ;;

            *)
                echo  "Invalid parameter: $1" 1>&2
                exit 1
                ;;
        esac
    done
}


# seperate ip and port
sep_ip_port() {
    # usage: sep_ip_port <ip:port> <var for ip> <var for port>
    # input <ip:port> can be:
    #   port (ip is 127.0.0.1)
    #   ipv4
    #   [ipv6]
    #   ipv4:port
    #   [ipv6]:port
    local IP
    local PORT
    local INPUT
    INPUT="$1"
    if (echo "$INPUT" | grep '\.' >/dev/null 2>&1) ;then  
        if (echo "$INPUT" | grep ':' >/dev/null 2>&1) ;then
            # ipv4 + port
            IP="$(echo $INPUT | cut -d: -f1)"
            PORT="$(echo $INPUT | cut -d: -f2)"
        else
            # ipv4
            IP="$INPUT"
        fi
    elif (echo "$INPUT" | grep '\]' >/dev/null 2>&1) ;then 
        if (echo "$INPUT" | grep '\]\:' >/dev/null 2>&1) ;then
            # ipv6 + port
            IP="$(echo $INPUT | cut -d']' -f1 | cut -d'[' -f2)"
            PORT="$(echo $INPUT | cut -d']' -f2 |cut -d: -f2)"
        else
            # ipv6
            IP="$(echo $INPUT | cut -d']' -f1 | cut -d'[' -f2)"
        fi
    else 
        # port
        IP='127.0.0.1'
        PORT="$INPUT"
    fi
    printf -v "$2" %s "$IP"
    printf -v "$3" %s "$PORT"
}

#=========================
is_interface() {
    [[ -z "$1" ]] && return 1
    [[ -d "/sys/class/net/${1}" ]]
}

is_vface_name_allocated(){
    is_interface "$1" || [[ -f "$COMMON_CONFDIR/vfaces/${1}" ]]
}

get_interface_phy_device() { # only for wifi interface
    local x
    for x in /sys/class/ieee80211/*; do
        [[ ! -e "$x" ]] && continue
        if [[ "${x##*/}" = "$1" ]]; then
            echo "$1"
            return 0
        elif [[ -e "$x/device/net/$1" ]]; then
            echo ${x##*/}
            return 0
        elif [[ -e "$x/device/net:$1" ]]; then
            echo ${x##*/}
            return 0
        fi
    done
    echo "Failed to get phy interface" >&2
    return 1
}

get_adapter_info() { # only for wifi interface
    local iPHY
    iPHY=$(get_interface_phy_device "$1")
    [[ $? -ne 0 ]] && return 1
    iw phy $iPHY info
}

get_adapter_kernel_module() {
    local MODULE
    MODULE=$(readlink -f "/sys/class/net/$1/device/driver/module")
    echo ${MODULE##*/}
}

can_be_sta_and_ap() {
    # iwconfig does not provide this information, assume false
    [[ $USE_IWCONFIG -eq 1 ]] && return 1
    if [[ "$(get_adapter_kernel_module "$1")" == "brcmfmac" ]]; then
        echo "WARN: brmfmac driver doesn't work properly with virtual interfaces and" >&2
        echo "      it can cause kernel panic. For this reason we disallow virtual" >&2
        echo "      interfaces for your adapter." >&2
        echo "      For more info: https://github.com/oblique/create_ap/issues/203" >&2
        return 1
    fi
    get_adapter_info "$1" | grep -E '{.* managed.* AP.*}' > /dev/null 2>&1 && return 0
    get_adapter_info "$1" | grep -E '{.* AP.* managed.*}' > /dev/null 2>&1 && return 0
    return 1
}

can_be_ap() {
    # iwconfig does not provide this information, assume true
    [[ $USE_IWCONFIG -eq 1 ]] && return 0
    get_adapter_info "$1" | grep -E '\* AP$' > /dev/null 2>&1 && return 0
    return 1
}

can_transmit_to_channel() {
    local IFACE CHANNEL_NUM CHANNEL_INFO
    IFACE=$1
    CHANNEL_NUM=$2

    if [[ $USE_IWCONFIG -eq 0 ]]; then
        if [[ $FREQ_BAND == 2.4 ]]; then
            CHANNEL_INFO=$(get_adapter_info ${IFACE} | grep " 24[0-9][0-9] MHz \[${CHANNEL_NUM}\]")
        else
            CHANNEL_INFO=$(get_adapter_info ${IFACE} | grep " \(49[0-9][0-9]\|5[0-9]\{3\}\) MHz \[${CHANNEL_NUM}\]")
        fi
        [[ -z "${CHANNEL_INFO}" ]] && return 1
        [[ "${CHANNEL_INFO}" == *no\ IR* ]] && return 1
        [[ "${CHANNEL_INFO}" == *disabled* ]] && return 1
        return 0
    else
        CHANNEL_NUM=$(printf '%02d' ${CHANNEL_NUM})
        CHANNEL_INFO=$(iwlist ${IFACE} channel | grep -E "Channel[[:blank:]]${CHANNEL_NUM}[[:blank:]]?:")
        [[ -z "${CHANNEL_INFO}" ]] && return 1
        return 0
    fi
}

# taken from iw/util.c
ieee80211_frequency_to_channel() {
    local FREQ=$1
    if [[ $FREQ -eq 2484 ]]; then
        echo 14
    elif [[ $FREQ -lt 2484 ]]; then
        echo $(( ($FREQ - 2407) / 5 ))
    elif [[ $FREQ -ge 4910 && $FREQ -le 4980 ]]; then
        echo $(( ($FREQ - 4000) / 5 ))
    elif [[ $FREQ -le 45000 ]]; then
        echo $(( ($FREQ - 5000) / 5 ))
    elif [[ $FREQ -ge 58320 && $FREQ -le 64800 ]]; then
        echo $(( ($FREQ - 56160) / 2160 ))
    else
        echo 0
    fi
}

is_5ghz_frequency() {
    [[ $1 =~ ^(49[0-9]{2})|(5[0-9]{3})$ ]]
}

is_interface_wifi_connected() {
    if [[ $USE_IWCONFIG -eq 0 ]]; then
        iw dev "$1" link 2>&1 | grep -E '^Connected to' > /dev/null 2>&1 && return 0
    else
        iwconfig "$1" 2>&1 | grep -E 'Access Point: [0-9a-fA-F]{2}:' > /dev/null 2>&1 && return 0
    fi
    return 1
}


is_unicast_macaddr() {
    local x
    x=$(echo "$1" | cut -d: -f1)
    x=$(printf '%d' "0x${x}")
    [[ $(expr $x % 2) -eq 0 ]]
}

get_interface_mac() {
    is_interface "$1" || return
    cat "/sys/class/net/${1}/address"
}

get_interface_pci_info() {  # pci id / model / virtual
    is_interface "$1" || return
    
    local device_path
    local pci_id
    local pci_full
    
    device_path="$(readlink -f /sys/class/net/$1)"
    
    if [[ "$device_path" == "/sys/devices/pci"* ]]; then
        pci_id="$(echo $device_path | sed 's/\//\n/g' | tail -n 3 |sed -n 1p)"
        
        if which lspci >/dev/null 2>&1 ; then
            pci_full="$( lspci -D -nn | grep -E "^$pci_id " )"
            echo "  PCI: $pci_full"
        else
            echo "  PCI: $pci_id"
        fi
    elif [[ "$device_path" == *"/virtual/"* ]]; then
        echo "  virtual interface"
    fi
    # TODO usb
    # TODO current driver
}

alloc_new_vface_name() { # only for wifi
    local i=0
    local v_iface_name="$VIRT_NAME"
    if [[ -z $VIRT_NAME ]]; then
        while :; do
            v_iface_name="x$i${WIFI_IFACE}"
            i=$((i + 1))
            is_vface_name_allocated ${v_iface_name} || break
        done
    fi
    mkdir -p $COMMON_CONFDIR/vfaces
    touch $COMMON_CONFDIR/vfaces/${v_iface_name}
    echo "${v_iface_name}"
}

dealloc_vface_name() {
    rm -f $COMMON_CONFDIR/vfaces/$1
}

#======

get_all_mac_in_system() {
    cat /sys/class/net/*/address
}

get_new_macaddr_according_to_existing() {
    local REALDEV OLDMAC NEWMAC LAST_BYTE i
    REALDEV=$1
    OLDMAC=$(get_interface_mac "$REALDEV")
    NEWMAC=""
    LAST_BYTE=$(printf %d 0x${OLDMAC##*:})
    for i in {10..240}; do
        NEWMAC="${OLDMAC%:*}:$(printf %02x $(( ($LAST_BYTE + $i) % 256 )))"
        (get_all_mac_in_system | grep "$NEWMAC" > /dev/null 2>&1) || break
    done
    echo "$NEWMAC"
}

generate_random_mac() {
    local r1 r2 r3 r4 r5 r6 
    local RAND_MAC
    while :; do
        r1=$( printf "%02x" $(($RANDOM%256/4*4)) )
        r2=$( printf "%02x" $(($RANDOM%256)) )
        r3=$( printf "%02x" $(($RANDOM%256)) )
        r4=$( printf "%02x" $(($RANDOM%256)) )
        r5=$( printf "%02x" $(($RANDOM%256)) )
        r6=$( printf "%02x" $(($RANDOM%256)) )
        RAND_MAC="$r1:$r2:$r3:$r4:$r5:$r6"
        ( ! ip link | grep "link" | grep $RAND_MAC > /dev/null 2>&1 ) && \
        ( ! ip maddress | grep "link" | grep $RAND_MAC > /dev/null 2>&1 ) && \
        ( ! ip neigh | grep "lladdr $RAND_MAC" > /dev/null 2>&1 ) && \
        ( ! get_all_mac_in_system | grep $RAND_MAC ) && \
        break
    done
    echo "$RAND_MAC"
}


is_ip4_lan_range_available() { # checks 192.168.x.x
    ( ip -4 address | grep "inet 192\.168\.$1\." > /dev/null 2>&1 ) && return 1
    ( ip -4 route | grep "^192\.168\.$1\." > /dev/null 2>&1 ) && return 1
    ( ip -4 route get 192.168.$1.0 2>&1 | grep -E "\bvia\b|\bunreachable\b" > /dev/null 2>&1 ) && \
    ( ip -4 route get 192.168.$1.255 2>&1 | grep  -E "\bvia\b|\bunreachable\b" > /dev/null 2>&1 )  && return 0
    return 1
}
is_ip6_lan_range_available() {  # checks fdxx::
    ( ip -6 address | grep -i "inet6 fd$1:$2$3:$4$5:$6$7:" > /dev/null 2>&1 ) && return 1
    ( ip -6 route | grep -i "^fd$1:$2$3:$4$5:$6$7:" > /dev/null 2>&1 ) && return 1
    ( ip -6 route get fd$1:$2$3:$4$5:$6$7:: 2>&1 | grep -E "\bvia\b|\bunreachable\b" > /dev/null 2>&1 ) && \
    ( ip -6 route get fd$1:$2$3:$4$5:$6$7:ffff:ffff:ffff:ffff 2>&1 | grep -E "\bvia\b|\bunreachable\b" > /dev/null 2>&1 )  && return 0
    return 1
}

generate_random_ip4() {
    local random_ip4
    while :; do
        random_ip4=$(($RANDOM%256))
        is_ip4_lan_range_available $random_ip4 && break
    done
    echo "192.168.$random_ip4.1"
}
generate_random_lan_ip6_prefix() {
    local r1 r2 r3 r4 r5 r6 r7
    while :; do
        r1=$( printf "%x" $(($RANDOM%240+16)) )
        r2=$( printf "%x" $(($RANDOM%240+16)) )
        r3=$( printf "%x" $(($RANDOM%240+16)) )
        r4=$( printf "%x" $(($RANDOM%240+16)) )
        r5=$( printf "%x" $(($RANDOM%240+16)) )
        r6=$( printf "%x" $(($RANDOM%240+16)) )
        r7=$( printf "%x" $(($RANDOM%240+16)) )
        is_ip6_lan_range_available $r1 $r2 $r3 $r4 $r5 $r6 $r7 && break
    done
    echo "fd$r1:$r2$r3:$r4$r5:$r6$r7::"
}



# start haveged when needed
haveged_watchdog() {
    local show_warn=1
    while :; do
        if [[ $(cat /proc/sys/kernel/random/entropy_avail) -lt 1000 ]]; then
            if ! which haveged > /dev/null 2>&1; then
                if [[ $show_warn -eq 1 ]]; then
                    echo "WARN: Low entropy detected. We recommend you to install \`haveged'" 1>&2
                    show_warn=0
                fi
            elif ! pidof haveged > /dev/null 2>&1; then # TODO judge zombie ?
                echo "Low entropy detected, starting haveged" 1>&2
                # boost low-entropy
                haveged -w 1024 -p $COMMON_CONFDIR/haveged.pid
            fi
        fi
        sleep 2
    done
}
pid_watchdog() {
    local PID="$1"
    local SLEEP="$2"
    local ERR_MSG="$3"
    local ST
    while true
    do 
        if [[ -e "/proc/$PID" ]]; then
            ST="$(cat "/proc/$PID/status" | grep "^State:" | awk '{print $2}')"
            if [[ "$ST" != 'Z' ]]; then
                sleep $SLEEP
                continue
            fi
        fi
        die "$ERR_MSG"
    done
    
}
#========


# only support NetworkManager >= 0.9.9
is_nm_running() {
    if (which nmcli >/dev/null 2>&1 ) && (nmcli -t -f RUNNING g 2>&1 | grep -E '^running$' >/dev/null 2>&1 ) ; then
        echo 1
    else
        echo 0
    fi
}

nm_knows() {
    (nmcli dev show $1 | grep -E "^GENERAL.STATE:" >/dev/null 2>&1 ) && return 0 # nm sees
    return 1 # nm doesn't see this interface
}
nm_get_manage() { # get an interface's managed state
    local s
    s=$(nmcli dev show $1 | grep -E "^GENERAL.STATE:") || return 2 # no such interface
    (echo $s | grep "unmanaged" >/dev/null 2>&1) && return 1 # unmanaged
    return 0 # managed
}
nm_set_unmanaged() {
    while ! nm_knows $1 ; do # wait for virtual wifi interface seen by NM
        sleep 0.5
    done
    if nm_get_manage $1 ;then
        echo "Set $1 unmanaged by NetworkManager"
        nmcli dev set $1 managed no || die "Failed to set $1 unmanaged by NetworkManager"
        NM_UNM_LIST=$1
        sleep 1
    fi
}

nm_set_managed() {
    nmcli dev set $1 managed yes
    NM_UNM_LIST=
}
nm_restore_manage() {
    if [[ $NM_UNM_LIST ]]; then
        echo "Restore $NM_UNM_LIST managed by NetworkManager"
        nm_set_managed $NM_UNM_LIST
        sleep 0.5
    fi
}
#=========
check_iptables()
{
    echo
    iptables --version
    
    if which firewall-cmd > /dev/null 2>&1; then
        if [[ "$(firewall-cmd --state 2>&1)" == "running" ]]; then
            echo "firewalld is running ($(firewall-cmd --version))"
            echo -e "\nWARN: We haven't completed the compatibility with firewalld.\nWARN: If you see any trouble, try:\nWARN:     1) 'firewall-cmd --zone=trusted --add-interface=<SUBN_IFACE>'\nWARN:     2) disable firewalld\n" >&2 
            # TODO
        fi
    fi
}

CUSTOM_CHAINS_4_filter=
CUSTOM_CHAINS_4_nat=
CUSTOM_CHAINS_6_filter=
CUSTOM_CHAINS_6_nat=
iptb() 
{
    local FoS=$1 # 4 | 6
    shift
    local Vis=$1 # 'v' | 'n'
    shift
    local T=$1 # table
    shift
    local ACT=$1 # action: I | A | N  .  On undo: I or A -> D , N -> F+X
    shift
    local CH=$1 # chain
    shift
    
    [[ "$IPV6" -ne 1 && "$FoS" == "6" ]] && return
    
    local CMD_HEAD=""
    local MOUTH=""
    local NECK=""
    local HAND_UN_NC=0
    local TAIL=""
    
    local FULL=""
    local ADD_TO_UNDO=1
    
    for arr_name in CUSTOM_CHAINS_4_filter CUSTOM_CHAINS_4_nat CUSTOM_CHAINS_6_filter CUSTOM_CHAINS_6_nat
    do
        local arr_content
        eval arr_content=\"\${$arr_name}\"
        #echo $arr_content
        
        for w in  $arr_content
        do
            if [[ "$arr_name" =~ "$FoS" && "$arr_name" =~ "$T" && "$w" == "$CH" ]]; then
                ADD_TO_UNDO=0
            fi
        done
    done
    

    [[ "$FoS" == "4" ]] && CMD_HEAD="iptables -w "
    [[ "$FoS" == "6" ]] && CMD_HEAD="ip6tables -w "
    
    [[ "$Vis" == 'v' ]] && MOUTH="-v"
    
    NECK="-t ${T}"
    
    if [[ "$ACT" == "N" ]]; then
        eval CUSTOM_CHAINS_${FoS}_${T}=\"\${CUSTOM_CHAINS_${FoS}_${T}} ${CH}\"
        HAND_UN_NC=1
    fi
    
    
    
    [[ ! "$NETFILTER_XT_MATCH_COMMENT" == "0" ]] && TAIL="-m comment --comment lrt${$}${SUBNET_IFACE}"
    
    if [[ "$ADD_TO_UNDO" -eq 1 ]]; then
        if [[ "$ACT" == "I" || "$ACT" == "A" ]]; then
            echo "$CMD_HEAD $NECK -D ${CH} $@ $TAIL" >> $CONFDIR/undo_iptables.sh 
        fi
        
        if [[ "$HAND_UN_NC" -eq 1 ]]; then
            echo "$CMD_HEAD $NECK -F ${CH} $@ $TAIL" >> $CONFDIR/undo_iptables_2.sh
            echo "$CMD_HEAD $NECK -X ${CH} $@ $TAIL" >> $CONFDIR/undo_iptables_2.sh
        fi
    fi
    
 
    

    FULL="$CMD_HEAD $MOUTH $NECK -${ACT} ${CH} $@ $TAIL"
    #echo $FULL
    $FULL
    return $?
}

start_nat() {
    if [[ $INTERNET_IFACE ]]; then
        IPTABLES_NAT_OUT="-o ${INTERNET_IFACE}"
        IPTABLES_NAT_IN="-i ${INTERNET_IFACE}"
        MASQUERADE_NOTOUT=""
    else
        MASQUERADE_NOTOUT="! -o ${SUBNET_IFACE}"
    fi
    echo
    echo "iptables: NAT "
    if [[ $NO4 -eq 0 ]]; then
        iptb 4 v nat I POSTROUTING -s ${GATEWAY%.*}.0/24 $IPTABLES_NAT_OUT $MASQUERADE_NOTOUT ! -d ${GATEWAY%.*}.0/24  -j MASQUERADE || die
        iptb 4 v filter I FORWARD  -i ${SUBNET_IFACE} $IPTABLES_NAT_OUT -s ${GATEWAY%.*}.0/24 -j ACCEPT || die
        iptb 4 v filter I FORWARD  -o ${SUBNET_IFACE} $IPTABLES_NAT_IN  -d ${GATEWAY%.*}.0/24 -j ACCEPT || die
    fi

        iptb 6 v nat I POSTROUTING  -s ${PREFIX6}/64 $IPTABLES_NAT_OUT $MASQUERADE_NOTOUT ! -d ${PREFIX6}/64  -j MASQUERADE || die
        iptb 6 v filter I FORWARD   -i ${SUBNET_IFACE} $IPTABLES_NAT_OUT -s ${PREFIX6}/64 -j ACCEPT || die
        iptb 6 v filter I FORWARD   -o ${SUBNET_IFACE} $IPTABLES_NAT_IN   -d ${PREFIX6}/64 -j ACCEPT || die
}

start_ban_lan() {
    echo
    echo "iptables: Disallow clients to access LAN"
    iptb 4 n filter N lrt${$}${SUBNET_IFACE}-BLF || die
    # TODO: allow '--dhcp-dns(6)' address port 53, which can be something needed, e.g. a VPN's internal private IP
    iptb 4 v filter I lrt${$}${SUBNET_IFACE}-BLF -d 0.0.0.0/8 -j REJECT || die # TODO: use array
    iptb 4 v filter I lrt${$}${SUBNET_IFACE}-BLF -d 10.0.0.0/8 -j REJECT || die
    iptb 4 v filter I lrt${$}${SUBNET_IFACE}-BLF -d 100.64.0.0/10 -j REJECT || die
    iptb 4 v filter I lrt${$}${SUBNET_IFACE}-BLF -d 127.0.0.0/8 -j REJECT || die
    iptb 4 v filter I lrt${$}${SUBNET_IFACE}-BLF -d 169.254.0.0/16 -j REJECT || die
    iptb 4 v filter I lrt${$}${SUBNET_IFACE}-BLF -d 172.16.0.0/12 -j REJECT || die
    iptb 4 v filter I lrt${$}${SUBNET_IFACE}-BLF -d 192.168.0.0/16 -j REJECT || die
    iptb 4 v filter I lrt${$}${SUBNET_IFACE}-BLF -d 224.0.0.0/4 -j REJECT || die
    iptb 4 v filter I lrt${$}${SUBNET_IFACE}-BLF -d 255.255.255.255 -j REJECT || die
    
    iptb 4 n filter I FORWARD -i ${SUBNET_IFACE} -j lrt${$}${SUBNET_IFACE}-BLF || die
    
    iptb 4 n filter N lrt${$}${SUBNET_IFACE}-BLI || die
    iptb 4 v filter I lrt${$}${SUBNET_IFACE}-BLI -i ${SUBNET_IFACE} ! -p icmp -j REJECT || die # ipv6 need icmp to function. TODO: maybe we can block some unneeded icmp to improve security
    
    iptb 4 n filter I INPUT -i ${SUBNET_IFACE} -j lrt${$}${SUBNET_IFACE}-BLI || die
    

    iptb 6 n filter N lrt${$}${SUBNET_IFACE}-BLF  || die
    iptb 6 v filter I lrt${$}${SUBNET_IFACE}-BLF -d fc00::/7 -j REJECT || die
    iptb 6 v filter I lrt${$}${SUBNET_IFACE}-BLF -d fe80::/10 -j REJECT || die
    iptb 6 v filter I lrt${$}${SUBNET_IFACE}-BLF -d ff00::/8 -j REJECT || die
    iptb 6 v filter I lrt${$}${SUBNET_IFACE}-BLF -d ::1 -j REJECT || die
    iptb 6 v filter I lrt${$}${SUBNET_IFACE}-BLF -d ::/128 -j REJECT || die
    iptb 6 v filter I lrt${$}${SUBNET_IFACE}-BLF -d ::ffff:0:0/96 -j REJECT || die
    iptb 6 v filter I lrt${$}${SUBNET_IFACE}-BLF -d ::ffff:0:0:0/96 -j REJECT || die

    iptb 6 n filter I FORWARD -i ${SUBNET_IFACE} -j lrt${$}${SUBNET_IFACE}-BLF || die
    
    iptb 6 n filter N lrt${$}${SUBNET_IFACE}-BLI  || die
    iptb 6 v filter I lrt${$}${SUBNET_IFACE}-BLI -i ${SUBNET_IFACE} ! -p icmpv6 -j REJECT || die

    iptb 6 n filter I INPUT -i ${SUBNET_IFACE} -j lrt${$}${SUBNET_IFACE}-BLI || die

}

allow_dns_port() {
    echo
    echo "iptables: allow DNS"
    iptb 4 v filter I INPUT -i ${SUBNET_IFACE} -s ${GATEWAY%.*}.0/24 -d ${GATEWAY} -p tcp -m tcp --dport 53 -j ACCEPT || die
    iptb 4 v filter I INPUT -i ${SUBNET_IFACE} -s ${GATEWAY%.*}.0/24 -d ${GATEWAY} -p udp -m udp --dport 53 -j ACCEPT || die
    iptb 6 v filter I INPUT -i ${SUBNET_IFACE} -s ${PREFIX6}/64 -d ${GATEWAY6} -p tcp -m tcp --dport 53 -j ACCEPT || die
    iptb 6 v filter I INPUT -i ${SUBNET_IFACE} -s ${PREFIX6}/64 -d ${GATEWAY6} -p udp -m udp --dport 53 -j ACCEPT || die
}


start_catch_dns() {
    echo
    echo "iptables: redirect DNS queries to this host"
    iptb 4 v nat I PREROUTING -i ${SUBNET_IFACE} ! -d ${GATEWAY} -p udp -m udp --dport 53 -j REDIRECT --to-ports 53 || die
    iptb 4 v nat I PREROUTING -i ${SUBNET_IFACE} ! -d ${GATEWAY} -p tcp -m tcp --dport 53 -j REDIRECT --to-ports 53 || die

    iptb 6 v nat I PREROUTING -i ${SUBNET_IFACE} ! -d ${GATEWAY6} -p udp -m udp --dport 53 -j REDIRECT --to-ports 53 || die
    iptb 6 v nat I PREROUTING -i ${SUBNET_IFACE} ! -d ${GATEWAY6} -p tcp -m tcp --dport 53 -j REDIRECT --to-ports 53 || die
}


allow_dhcp() {
    echo 
    echo "iptables: allow dhcp"
    
    iptb 4 v filter I INPUT -i ${SUBNET_IFACE} -p udp -m udp --dport 67 -j ACCEPT || die
    iptb 6 v filter I INPUT -i ${SUBNET_IFACE} -p udp -m udp --dport 547 -j ACCEPT || die
}

# TODO: use 'DNAT' instead of '--to-ports' to support other IP
start_redsocks() {
    echo
    echo "iptables: transparent proxy non-LAN TCP and UDP(not tested) traffic to port ${TP_PORT}"
    if [[ $NO4 -eq 0 ]]; then
        iptb 4 n nat N lrt${$}${SUBNET_IFACE}-TP || die
        iptb 4 n nat A lrt${$}${SUBNET_IFACE}-TP -d 0.0.0.0/8 -j RETURN || die
        iptb 4 n nat A lrt${$}${SUBNET_IFACE}-TP -d 10.0.0.0/8 -j RETURN || die
        iptb 4 n nat A lrt${$}${SUBNET_IFACE}-TP -d 100.64.0.0/10  -j RETURN || die
        iptb 4 n nat A lrt${$}${SUBNET_IFACE}-TP -d 127.0.0.0/8 -j RETURN || die
        iptb 4 n nat A lrt${$}${SUBNET_IFACE}-TP -d 169.254.0.0/16 -j RETURN || die
        iptb 4 n nat A lrt${$}${SUBNET_IFACE}-TP -d 172.16.0.0/12 -j RETURN || die
        iptb 4 n nat A lrt${$}${SUBNET_IFACE}-TP -d 192.168.0.0/16 -j RETURN || die
        iptb 4 n nat A lrt${$}${SUBNET_IFACE}-TP -d 224.0.0.0/4 -j RETURN || die
        iptb 4 n nat A lrt${$}${SUBNET_IFACE}-TP -d 255.255.255.255 -j RETURN || die
        
        iptb 4 v nat A lrt${$}${SUBNET_IFACE}-TP -p tcp -j REDIRECT --to-ports ${TP_PORT} || die
        iptb 4 v nat A lrt${$}${SUBNET_IFACE}-TP -p udp -j REDIRECT --to-ports ${TP_PORT} || die

        iptb 4 v nat I PREROUTING -i ${SUBNET_IFACE} -s ${GATEWAY%.*}.0/24 -j lrt${$}${SUBNET_IFACE}-TP || die

        iptb 4 v filter I INPUT -i ${SUBNET_IFACE} -s ${GATEWAY%.*}.0/24 -p tcp -m tcp --dport ${TP_PORT}  -j ACCEPT || die
        iptb 4 v filter I INPUT -i ${SUBNET_IFACE} -s ${GATEWAY%.*}.0/24 -p udp -m udp --dport ${TP_PORT}  -j ACCEPT || die
    fi

        iptb 6 n nat N lrt${$}${SUBNET_IFACE}-TP || die
        iptb 6 n nat A lrt${$}${SUBNET_IFACE}-TP -d fc00::/7 -j RETURN || die
        iptb 6 n nat A lrt${$}${SUBNET_IFACE}-TP -d fe80::/10 -j RETURN || die
        iptb 6 n nat A lrt${$}${SUBNET_IFACE}-TP -d ff00::/8 -j RETURN || die
        iptb 6 n nat A lrt${$}${SUBNET_IFACE}-TP -d ::1 -j RETURN || die
        iptb 6 n nat A lrt${$}${SUBNET_IFACE}-TP -d :: -j RETURN || die

        iptb 6 v nat A lrt${$}${SUBNET_IFACE}-TP -p tcp -j REDIRECT --to-ports ${TP_PORT} || die
        iptb 6 v nat A lrt${$}${SUBNET_IFACE}-TP -p udp -j REDIRECT --to-ports ${TP_PORT} || die

        iptb 6 v nat I PREROUTING -i ${SUBNET_IFACE} -s ${PREFIX6}/64 -j lrt${$}${SUBNET_IFACE}-TP || die

        iptb 6 v filter I INPUT -i ${SUBNET_IFACE} -s ${PREFIX6}/64 -p tcp -m tcp --dport ${TP_PORT}  -j ACCEPT || die
        iptb 6 v filter I INPUT -i ${SUBNET_IFACE} -s ${PREFIX6}/64 -p udp -m udp --dport ${TP_PORT}  -j ACCEPT || die   

}

#---------------------------------------
backup_ipv6_bits() {
    mkdir "$CONFDIR/sys_6_conf_iface" || die "Failed making dir to save interface IPv6 status"
    cp  "/proc/sys/net/ipv6/conf/$SUBNET_IFACE/disable_ipv6" \
        "/proc/sys/net/ipv6/conf/$SUBNET_IFACE/accept_ra"     \
        "/proc/sys/net/ipv6/conf/$SUBNET_IFACE/use_tempaddr"  \
        "/proc/sys/net/ipv6/conf/$SUBNET_IFACE/addr_gen_mode" \
            "$CONFDIR/sys_6_conf_iface/" || die "Failed backing up interface ipv6 bits"
            
    if [[ "$SHARE_METHOD" == 'redsocks' ]] ; then
        cp "/proc/sys/net/ipv6/conf/$SUBNET_IFACE/forwarding" \
            "$CONFDIR/sys_6_conf_iface/" || die "Failed backking up interface ipv6 bits"
    fi
}
set_ipv6_bits() {
    if [[ $IPV6 -eq 1 ]]; then
        echo 0 > "/proc/sys/net/ipv6/conf/$SUBNET_IFACE/disable_ipv6"
        echo 0 > "/proc/sys/net/ipv6/conf/$SUBNET_IFACE/accept_ra"
        echo 0 > "/proc/sys/net/ipv6/conf/$SUBNET_IFACE/use_tempaddr"
        echo 0 > "/proc/sys/net/ipv6/conf/$SUBNET_IFACE/addr_gen_mode"
    else
        echo 1 > "/proc/sys/net/ipv6/conf/$SUBNET_IFACE/disable_ipv6"
    fi
}
restore_ipv6_bits() {
    if [[ -d "$CONFDIR/sys_6_conf_iface" ]]; then
        cp -f "$CONFDIR/sys_6_conf_iface/*" "/proc/sys/net/ipv6/conf/$SUBNET_IFACE/"
    fi
}

set_interface_mac() {
    local INTERFACE
    local MAC
    
    INTERFACE=$1
    MAC=$2
    
    ip link set dev ${INTERFACE} address ${MAC} 
}

backup_interface_status() {
    # virtual wifi interface will be destroyed, so no need to save status
    
    # backup interface up or down status
    (ip link show ${SUBNET_IFACE} |grep -q "state UP") && SUBNET_IFACE_ORIGINAL_UP_STATUS=1
    
    # save interface old mac 
    #if [[ -n "$NEW_MACADDR" ]]; then 
        OLD_MACADDR=$(get_interface_mac $SUBNET_IFACE)
        #echo "Saved ${SUBNET_IFACE} old MAC address ${OLD_MACADDR} into RAM"
    #fi
    
    backup_ipv6_bits
    
    # TODO : ? backup ip and others???
    
    # nm managing status is saved when nm_set_unmanaged()
}
restore_interface_status() {
    # virtual wifi interface will be destroyed, so no need to restore status
    # don't use [[ $VWIFI_IFACE ]] to judge, if creating virtual wifi failed, VWIFI_IFACE is empty
    [[ "$WIFI_IFACE" && "$NO_VIRT" -eq 0 ]] && return
    
    restore_ipv6_bits

    if [[ -n "$OLD_MACADDR" && "$(get_interface_mac $SUBNET_IFACE)" != "$OLD_MACADDR" ]] ; then
        echo "Restoring ${SUBNET_IFACE} to old MAC address ${OLD_MACADDR} ..."
        set_interface_mac ${SUBNET_IFACE} ${OLD_MACADDR} || echo "Failed restoring ${SUBNET_IFACE} to old MAC address ${OLD_MACADDR}" >&2
    fi
    
    nm_restore_manage
    
    [[ $SUBNET_IFACE_ORIGINAL_UP_STATUS -eq 1 ]] && ip link set up dev ${SUBNET_IFACE} && echo "Restore ${SUBNET_IFACE} to link up"
}
#---------------------------------------

kill_processes() { # for this instance
    #echo "Killing processes"
    local x  pid
    for x in $CONFDIR/*.pid; do
        # even if the $CONFDIR is empty, the for loop will assign
        # a value in $x. so we need to check if the value is a file
        if [[ -f $x ]] &&  sleep 0.3  && [[ -f $x ]]; then
            pid=$(cat $x)
            pn=$( ps -p $pid -o comm= ) 
            #echo "Killing $pid $pn ... "
            pkill -P $pid
            kill $pid 2>/dev/null && ( echo "Killed $(basename $x) $pid $pn" && rm $x ) || echo "Failed to kill $(basename $x) $pid $pn, it may have exited"
        fi
    done
}

_cleanup() {
    local x

    ip addr flush ${SUBNET_IFACE}
    
    rm -rf $CONFDIR
    
    ip link set down dev ${SUBNET_IFACE}
    
    if [[ $VWIFI_IFACE ]]; then # the subnet interface (virtual wifi interface) will be removed
        iw dev ${VWIFI_IFACE} del
        dealloc_vface_name $VWIFI_IFACE
    fi
    
    restore_interface_status
    
    if ! has_running_instance; then
        echo "Exiting: This is the only running instance"
        # kill common processes
        for x in $COMMON_CONFDIR/*.pid; do
            [[ -f $x ]] && kill -9 $(cat $x) && rm $x
        done
        
        rm -d $COMMON_CONFDIR/vfaces
        rm -d $COMMON_CONFDIR
        rm -d $TMPDIR
    else
        echo "Exiting: This is NOT the only running instance"
    fi
}

clean_iptables() {
    [[ -f $CONFDIR/undo_iptables.sh ]] && bash $CONFDIR/undo_iptables.sh
    
    [[ -f $CONFDIR/undo_iptables_2.sh ]] && bash $CONFDIR/undo_iptables_2.sh
}

cleanup() {
    trap "" SIGINT SIGUSR1 SIGUSR2 EXIT SIGTERM
    echo
    echo
    echo "Doing cleanup.. "
    kill_processes
    echo "Undoing iptables changes .."
    clean_iptables > /dev/null
    _cleanup 2> /dev/null
    
    #pgid=$(ps opgid= $$ |awk '{print $1}' )
    #echo "Killing PGID $pgid ..."
    #kill -15 -$pgid
    #sleep 1 
    echo "Cleaning up done"
    #kill -9 -$pgid
}

# NOTE function die() is designed NOT to be used before init_trap() executed
die() { # SIGUSR2
    echo "Error occured"
    [[ -n "$1" ]] && echo -e "\nERROR: $1\n" >&2
    # send die signal to the main process
    [[ $BASHPID -ne $$ ]] && kill -USR2 $$ || cleanup
    exit 1
}

clean_exit() { # SIGUSR1
    # send clean_exit signal to the main process
    [[ $BASHPID -ne $$ ]] && kill -USR1 $$ || cleanup
    exit 0
}

init_trap(){
    trap "cleanup" EXIT
    trap "clean_exit" SIGINT SIGUSR1 SIGTERM
    trap "die" SIGUSR2
}
init_conf_dirs() {
    mkdir -p "$TMPDIR" || die "Couldn't make linux-router's temporary dir"
    chmod 755 "$TMPDIR" 2>/dev/null
    cd "$TMPDIR" || die "Couldn't change directory to linux-router's temporary path"

    CONFDIR="$(mktemp -d $TMPDIR/lnxrouter.${TARGET_IFACE}.conf.XXXXXX)" || die "Instance couldn't make config dir" # config dir for one instance
    chmod 755 "$CONFDIR"
    #echo "Config dir: $CONFDIR"
    echo $$ > "$CONFDIR/pid"

    COMMON_CONFDIR="$TMPDIR/lnxrouter_common.conf" # config dir for all instances
    mkdir -p "$COMMON_CONFDIR"
}

#== functions to deal with running instances

list_running_conf() {
    local x
    for x in $TMPDIR/lnxrouter.*; do
        if [[ -f $x/pid && -f $x/subn_iface && -d /proc/$(cat $x/pid) ]]; then
            echo "$x"
        fi
    done
}

list_running() {
    local IFACE subn_iface x
    for x in $(list_running_conf); do
        IFACE=${x#*.}
        IFACE=${IFACE%%.*}
        subn_iface=$(cat $x/subn_iface)

        if [[ $IFACE == $subn_iface ]]; then
            echo $(cat $x/pid) $IFACE
        else
            echo $(cat $x/pid) $IFACE '('$(cat $x/subn_iface)')'
        fi
    done
}

get_subn_iface_from_pid() {
    list_running | awk '{print $1 " " $NF}' | tr -d '\(\)' | grep -E "^${1} " | cut -d' ' -f2
}

get_pid_from_subn_iface() {
    list_running | awk '{print $1 " " $NF}' | tr -d '\(\)' | grep -E " ${1}$" | cut -d' ' -f1
}

get_confdir_from_pid() {
    local IFACE x
    for x in $(list_running_conf); do
        if [[ $(cat $x/pid) == "$1" ]]; then
            echo "$x"
            break
        fi
    done
}

#======================================================

print_clients_from_leases() {  # MAC|IP|HOST|lease
    local LEASE_FILE="$1"
    local FILEC
    local line
    local LEASEstr LEASEstamp
    
    FILEC="$(cat "$LEASE_FILE" | grep -v -E "^duid\b" | sed -r '/^\s*$/d' )"

    # TODO: duid is somewhat related to ipv6. I don't know about it. Not sure excluding it miss some info or not
    echo "$FILEC" | while read line
    do
        #echo aa$line
        LEASEstamp="$(echo "$line" | awk '{print $1}')"
        MAC="$(echo "$line" | awk '{print $2}')"
        IP="$(echo "$line" | awk '{print $3}'  | sed 's/\[//g' | sed 's/\]//g')"
        HOST="$(echo "$line" | awk '{print $4}' | sed 's/*/?/g' | sed 's/|/_/g' | sed 's/ /_/g' )"
        
        if [[ -n "$MAC" ]]; then
            LEASEstr="$(date -d @${LEASEstamp} +%m-%d_%X)"
            
            echo "$MAC|$IP|$HOST|lease_$LEASEstr"
        fi
    done
    
}
print_interface_neighbors_via_iproute() {  # MAC|IP|_|STATUS 
    local IFACE=$1
    
    local line
    
    ip n | grep -E "\bdev $IFACE\b" | sed 's/ /|/g' | while read line
    do
        local MAC IP STATUS
        
        IP="$(echo $line | awk -F'|' '{print $1}')"
        
        if [[ "$(echo $line | awk -F'|' '{print $4}')" == "lladdr" ]]; then # has mac
            # if has mac, $4="lladdr" and $5=macaddress and $6+=status
            MAC="$(echo $line | awk -F'|' '{print $5}')"
            STATUS="$(echo $line | awk -F'|' '$1="";$2="";$3="";$4="";$5="";{print}' | awk '{$1=$1;print}'| sed 's/ /,/g')"
        else # no mac 
            # if no mac, $4="" and $5+=status
            MAC="?"
            STATUS="$(echo $line | awk -F'|' '$1="";$2="";$3="";$4="";{print}' | awk '{$1=$1;print}' | sed 's/ /,/g')"
        fi
        if [[ -n "$IP" && ( "$MAC" != "?" || "$STATUS" != "FAILED" ) ]]; then
            echo "$MAC|$IP|?|$STATUS"
        fi
    done
}
print_interface_neighbors_via_iw() {  # MAC|_|_|signal  
    local IFACE=$1
    local MAC SIGNAL
    iw dev $IFACE station dump | awk '($1 ~ /Station$/) {print $2}' | while read MAC
    do
        if [[ -n "$MAC" ]]; then
            SIGNAL="$(iw dev $IFACE station get $MAC | grep "signal:" | awk '{print $2}')"
            echo "${MAC}|?|?|${SIGNAL}_dBm"
        fi
    done
}

list_clients() { # passive mode. (use 'arp-scan' or 'netdiscover' if want active mode)
    local IFACE pid
    local CONFDIR
    
    local output=""
    # If number (PID) is given, get the associated wifi iface
    if [[ "$1" =~ ^[1-9][0-9]*$ ]]; then
        pid="$1"
        IFACE=$(get_subn_iface_from_pid "$pid")
        if [[ -z "$IFACE" ]] ; then
            echo "'$pid' is not the pid of a running $PROGNAME instance." >&2 
            exit 1
        fi
    else # non-number given
        IFACE="$1"
        if ( ! is_interface $IFACE ) ; then
            echo "'$IFACE' is not an interface or PID" >&2
            exit 1
        fi
        pid=$(get_pid_from_subn_iface "$IFACE")
        if [[ -n "$pid" ]] ; then  # if this interface is hosted by us
            CONFDIR=$(get_confdir_from_pid "$pid")
            output="$(print_clients_from_leases "$CONFDIR/dnsmasq.leases" )"
        else    # this interface NOT hosted by us
            echo "Tip: '$IFACE' is not an interface hosted by $PROGNAME" >&2
        fi
    fi
    output="$(echo "$output" ; print_interface_neighbors_via_iw $IFACE) "
    output="$(echo "$output" ; print_interface_neighbors_via_iproute $IFACE)"
    
    output="$(echo "$output" | sort -k 1 -k 2 -t '|' | uniq | sed -r '/^\s*$/d')"

    echo "$IFACE ($(get_interface_mac $IFACE)) neighbors:"
    
    local fmt="%-19s%-41s%-20s%s" # string length: MAC 17, ipv4 15, ipv6 39, hostname ?
    printf "$fmt\n"  "MAC" "IP" "HOSTNAME" "INFO"
    
    local line
    echo "$output"| while read line
    do
        if [[ -n "$line" ]]; then
            echo "$line" | awk -F'|' "{printf \"$fmt\n\",\$1,\$2,\$3,\$4}"
        fi
    done
    # TODO : merge same mac and same ip line
}

has_running_instance() {
    local PID x

    for x in $TMPDIR/lnxrouter.*; do
        if [[ -f $x/pid ]]; then
            PID=$(cat $x/pid)
            if [[ -d /proc/$PID ]]; then
                return 0
            fi
        fi
    done

    return 1
}

is_running_pid() {
    list_running | grep -E "^${1} " > /dev/null 2>&1
}

send_stop() {
    local x

    # send stop signal to specific pid
    if is_running_pid $1; then
        kill -USR1 $1
        return
    fi

    # send stop signal to specific interface
    for x in $(list_running | grep -E " \(?${1}( |\)?\$)" | cut -f1 -d' '); do
        kill -USR1 $x
    done
}


## ========================================================
## ========================================================
# decide linux-router's global temporary path for all instances
# this is different and should be before config-saving dir. The latter is for one instance
decide_tmpdir(){
    local TMPD
    if [[ -d /dev/shm ]]; then
        TMPD=/dev/shm
    elif [[ -d /run/shm ]]; then
        TMPD=/run/shm
    else
        TMPD=/tmp
    fi
    #TMPDIR=$TMPD/lnxrouter_tmp
    echo "$TMPD/lnxrouter_tmp"
}

#======

check_other_functions(){
    if [[ $LIST_RUNNING -eq 1 ]]; then
        echo -e "List of running $PROGNAME instances:\n"
        list_running
        exit 0
    fi

    if [[ -n "$LIST_CLIENTS_ID" ]]; then
        list_clients "$LIST_CLIENTS_ID"
        exit 0
    fi

    ##### root test ##### NOTE above don't require root ##########
    if [[ $(id -u) -ne 0 ]]; then
        echo "ERROR: Need root to continue" >&2
        exit 1
    fi
    ###### NOTE below require root ##########

    if [[ -n "$STOP_ID" ]]; then
        echo "Trying to kill $PROGNAME instance associated with $STOP_ID..."
        send_stop "$STOP_ID"
        exit 0
    fi
}


daemonizing_check(){
    if [[ $DAEMONIZE -eq 1 && $RUNNING_AS_DAEMON -eq 0 ]]; then
        echo "Running as Daemon..."
        # run a detached lnxrouter
        RUNNING_AS_DAEMON=1 setsid "$0" "${ARGS[@]}" &
        exit 0
    fi
}

#============================
check_wifi_settings() {

    if ! ( which iw > /dev/null 2>&1 && iw dev $WIFI_IFACE info > /dev/null 2>&1 ); then
        echo "WARN: Can't use 'iw' to operate interfce '$WIFI_IFACE', trying 'iwconfig' (not as good as 'iw') ..." >&2
        USE_IWCONFIG=1
    fi
    
    if [[ $USE_IWCONFIG -eq 1 ]]; then
        if ! (which iwconfig > /dev/null 2>&1 && iwconfig $WIFI_IFACE > /dev/null 2>&1); then
            echo "ERROR: Can't use 'iwconfig' to operate interfce '$WIFI_IFACE'" >&2
            exit 1
        fi
    fi
    
    if [[ $FREQ_BAND != 2.4 && $FREQ_BAND != 5 ]]; then
        echo "ERROR: Invalid frequency band" >&2
        exit 1
    fi

    if [[ $CHANNEL == default ]]; then
        if [[ $FREQ_BAND == 2.4 ]]; then
            CHANNEL=1
        else
            CHANNEL=36
        fi
    fi

    if [[ $FREQ_BAND != 5 && $CHANNEL -gt 14 ]]; then
        echo "Channel number is greater than 14, assuming 5GHz frequency band"
        FREQ_BAND=5
    fi

    if ! can_be_ap ${WIFI_IFACE}; then
        echo "ERROR: Your adapter does not support AP (master) mode" >&2
        exit 1
    fi

    if ! can_be_sta_and_ap ${WIFI_IFACE}; then
        if is_interface_wifi_connected ${WIFI_IFACE}; then
            echo "ERROR: Your adapter can not be a station (i.e. be connected) and an AP at the same time" >&2
            exit 1
        elif [[ $NO_VIRT -eq 0 ]]; then
            echo "WARN: Your adapter does not fully support AP virtual interface, enabling --no-virt" >&2
            NO_VIRT=1
        fi
    fi

    HOSTAPD=$(which hostapd)

    if [[ $(get_adapter_kernel_module ${WIFI_IFACE}) =~ ^(8192[cd][ue]|8723a[sue])$ ]]; then
        if ! strings "$HOSTAPD" | grep -m1 rtl871xdrv > /dev/null 2>&1; then
            echo "ERROR: You need to patch your hostapd with rtl871xdrv patches." >&2
            exit 1
        fi

        if [[ $DRIVER != "rtl871xdrv" ]]; then
            echo "WARN: Your adapter needs rtl871xdrv, enabling --driver=rtl871xdrv" >&2
            DRIVER=rtl871xdrv
        fi
    fi
    
    if [[ ${#SSID} -lt 1 || ${#SSID} -gt 32 ]]; then
        echo "ERROR: Invalid SSID length ${#SSID} (expected 1..32)" >&2
        exit 1
    fi

    if [[ $USE_PSK -eq 0 ]]; then
        if [[ ${#PASSPHRASE} -gt 0 && ${#PASSPHRASE} -lt 8 ]] || [[ ${#PASSPHRASE} -gt 63 ]]; then
            echo "ERROR: Invalid passphrase length ${#PASSPHRASE} (expected 8..63)" >&2
            exit 1
        fi
    elif [[ ${#PASSPHRASE} -gt 0 && ${#PASSPHRASE} -ne 64 ]]; then
        echo "ERROR: Invalid pre-shared-key length ${#PASSPHRASE} (expected 64)" >&2
        exit 1
    fi

    if [[ $(get_adapter_kernel_module ${WIFI_IFACE}) =~ ^rtl[0-9].*$ ]]; then
        if [[ $WPA_VERSION == '1' || $WPA_VERSION == '1+2' ]]; then
            echo "WARN: Realtek drivers usually have problems with WPA1, WPA2 is recommended" >&2
        fi
        echo "WARN: If AP doesn't work, read https://github.com/oblique/create_ap/blob/master/howto/realtek.md" >&2
    fi

    if [[ -z $VIRT_NAME ]]; then
        if [[ ${#WIFI_IFACE} -gt 13 ]]; then
            echo "WARN: $WIFI_IFACE has ${#WIFI_IFACE} characters which might be too long. If AP doesn't work, see --virt-name and https://github.com/garywill/linux-router/issues/44" >&2
        fi
    elif [[ ${#VIRT_NAME} -gt 15 ]]; then
        echo "WARN: option --virt-name $VIRT_NAME has ${#VIRT_NAME} characters which might be too long, consider making it shorter in case of errors" >&2
    fi

    if [[ ! -z $VIRT_NAME ]] && is_vface_name_allocated $VIRT_NAME; then
      echo "WARN: interface $VIRT_NAME aleady exists, this will cause an error"
    fi
}

check_if_new_mac_valid() {
    if ! is_unicast_macaddr "$NEW_MACADDR"; then
        echo "ERROR: The first byte of MAC address (${NEW_MACADDR}) must be even" >&2
        exit 1
    fi

    if [[ $(get_all_mac_in_system | grep -c ${NEW_MACADDR}) -ne 0 ]]; then
        echo "WARN: MAC address '${NEW_MACADDR}' already exists" >&2
    fi
}

decide_target_interface() {
    # TARGET_IFACE is a existing physical interface
    if [[ "$CONN_IFACE" ]]; then
        echo "$CONN_IFACE"
    elif [[ "$WIFI_IFACE" ]]; then
        echo "$WIFI_IFACE"
    else
        echo "No target interface specified"  >&2
        return 1
    fi
}

decide_ip_addresses() {
    if [[ ! -n $GATEWAY ]]; then
        GATEWAY="$(generate_random_ip4)"
        echo "Use random LAN IPv4 address $GATEWAY"
    elif [[ ! "$GATEWAY" =~ "." ]]; then
        GATEWAY="192.168.${GATEWAY}.1"
    fi

    if [[ $IPV6 -eq 1 && ! -n $PREFIX6 ]]; then
        PREFIX6="$(generate_random_lan_ip6_prefix)"
        echo "Use random LAN IPv6 address ${PREFIX6}${IID6}"
    elif [[ ! "$PREFIX6" =~ ":" ]]; then
        PREFIX6="fd00:0:0:${PREFIX6}::"
    fi
    if [[ $IPV6 -eq 1 ]]; then
        GATEWAY6="${PREFIX6}${IID6}"
    fi
}

prepare_wifi_interface() {
    if [[ $USE_IWCONFIG -eq 0 ]]; then
        iw dev ${WIFI_IFACE} set power_save off
    fi
    
    if [[ $NO_VIRT -eq 0 ]]; then
    ## Will generate virtual wifi interface
        if is_interface_wifi_connected ${WIFI_IFACE}; then
            WIFI_IFACE_FREQ=$(iw dev ${WIFI_IFACE} link | grep -i freq | awk '{print $2}')
            WIFI_IFACE_CHANNEL=$(ieee80211_frequency_to_channel ${WIFI_IFACE_FREQ})
            echo "${WIFI_IFACE} already in channel ${WIFI_IFACE_CHANNEL} (${WIFI_IFACE_FREQ} MHz)"
            if is_5ghz_frequency $WIFI_IFACE_FREQ; then
                FREQ_BAND=5
            else
                FREQ_BAND=2.4
            fi
            if [[ $WIFI_IFACE_CHANNEL -ne $CHANNEL ]]; then
                echo "Channel fallback to ${WIFI_IFACE_CHANNEL}"
                CHANNEL=$WIFI_IFACE_CHANNEL
            else
                echo
            fi
        fi

        echo "Creating a virtual WiFi interface... "
        VWIFI_IFACE=$(alloc_new_vface_name)
        if iw dev ${WIFI_IFACE} interface add ${VWIFI_IFACE} type __ap; then
            # Successfully created virtual wifi interface
            # if NM running, it will give the new virtual interface a random MAC. MAC will go back after setting NM unmanaged
            sleep 2  
            echo "${VWIFI_IFACE} created"
        else
            VWIFI_IFACE=
            if [[ ! -z ${VIRT_NAME} ]] && [[ ${#VIRT_NAME} -gt 15 ]]; then
              die "Failed creating virtual WiFi interface. This is likely because you have set a long name for your virtual interface using --virt-name, try making it shorter'"
            elif [[ -z ${VIRT_NAME} ]] && [[ ${#WIFI_IFACE} -gt 13 ]]; then
              die "Failed creating virtual WiFi interface. This is likely because your interface name is too long. Try using '--virt-name <shorter interface name>'"
            else
              die "Failed creating virtual WiFi interface. Maybe your WiFi adapter does not fully support virtual interfaces. Try again with '--no-virt'"
            fi
        fi
        
        AP_IFACE=${VWIFI_IFACE}
    else # no virtual wifi interface, use wifi device interface itself
        AP_IFACE=${WIFI_IFACE}
    fi
}

decide_subnet_interface() {
    if [[ $WIFI_IFACE ]]; then
        echo "${AP_IFACE}"
    else
        echo "${TARGET_IFACE}"
    fi
}

dealwith_mac() {
    local VMAC
    
    if [[ -n "$NEW_MACADDR" ]] ; then  # user choose to set subnet mac 

        echo "Setting ${SUBNET_IFACE} new MAC address ${NEW_MACADDR} ..."
        set_interface_mac ${SUBNET_IFACE} ${NEW_MACADDR} || die "Failed setting new MAC address"
        
    elif [[ $VWIFI_IFACE ]]; then # user didn't choose to set mac, but using virtual wifi interface

        VMAC=$(get_new_macaddr_according_to_existing ${WIFI_IFACE})
        if [[ "$VMAC" ]]; then
            echo "Assigning MAC address $VMAC to virtual interface $VWIFI_IFACE according to $WIFI_IFACE ..."
            set_interface_mac $VWIFI_IFACE $VMAC
        fi
    fi
}

write_hostapd_conf() {  
    cat <<- EOF > "$CONFDIR/hostapd.conf"
		beacon_int=100
		ssid=${SSID}
		interface=${AP_IFACE}
		driver=${DRIVER}
		channel=${CHANNEL}
		ctrl_interface=$CONFDIR/hostapd_ctrl
		ctrl_interface_group=0
		ignore_broadcast_ssid=$HIDDEN
		ap_isolate=$ISOLATE_CLIENTS
	EOF

    if [[ -n "$COUNTRY" ]]; then
        cat <<- EOF >> "$CONFDIR/hostapd.conf"
			country_code=${COUNTRY}
			ieee80211d=1
		EOF
    fi

    if [[ $FREQ_BAND == 2.4 ]]; then
        echo "hw_mode=g" >> "$CONFDIR/hostapd.conf"
    else
        echo "hw_mode=a" >> "$CONFDIR/hostapd.conf"
    fi

    if [[ $MAC_FILTER -eq 1 ]]; then
        cat <<- EOF >> "$CONFDIR/hostapd.conf"
			macaddr_acl=${MAC_FILTER}
			accept_mac_file=${MAC_FILTER_ACCEPT}
		EOF
    fi

    if [[ $IEEE80211N -eq 1 ]]; then
        cat <<- EOF >> "$CONFDIR/hostapd.conf"
			ieee80211n=1
			ht_capab=${HT_CAPAB}
		EOF
    fi

    if [[ $IEEE80211AC -eq 1 ]]; then
        echo "ieee80211ac=1" >> "$CONFDIR/hostapd.conf"
    fi

    if [[ -n "$VHT_CAPAB" ]]; then
        echo "vht_capab=${VHT_CAPAB}" >> "$CONFDIR/hostapd.conf"
    fi

    if [[ $IEEE80211N -eq 1 ]] || [[ $IEEE80211AC -eq 1 ]]; then
        echo "wmm_enabled=1" >> "$CONFDIR/hostapd.conf"
    fi

    if [[ -n "$PASSPHRASE" ]]; then
        [[ "$WPA_VERSION" == "1+2" ]] && WPA_VERSION=3
        if [[ $USE_PSK -eq 0 ]]; then
            WPA_KEY_TYPE=passphrase
        else
            WPA_KEY_TYPE=psk
        fi
        cat <<- EOF >> "$CONFDIR/hostapd.conf"
			wpa=${WPA_VERSION}
			wpa_${WPA_KEY_TYPE}=${PASSPHRASE}
			wpa_key_mgmt=WPA-PSK
			wpa_pairwise=CCMP
			rsn_pairwise=CCMP
		EOF
    else
        echo "WARN: WiFi is not protected by password" >&2
    fi
    chmod 600 "$CONFDIR/hostapd.conf"
}

write_dnsmasq_conf() {
    if grep "^nobody:" /etc/group >/dev/null 2>&1 ; then
        NOBODY_GROUP="nobody"
    else
        NOBODY_GROUP="nogroup"
    fi
    
    mkfifo "$CONFDIR/dnsmasq.log" || die "Failed creating pipe file for dnsmasq"
    chown nobody "$CONFDIR/dnsmasq.log" || die "Failed changing dnsmasq log file owner"
    cat "$CONFDIR/dnsmasq.log" & 
    
    cat <<- EOF > "$CONFDIR/dnsmasq.conf"
		user=nobody
		group=$NOBODY_GROUP
		bind-dynamic
		listen-address=${GATEWAY}
		interface=$SUBNET_IFACE
		except-interface=lo
		no-dhcp-interface=lo
		dhcp-range=${GATEWAY%.*}.10,${GATEWAY%.*}.250,255.255.255.0
		dhcp-option-force=option:router,${GATEWAY}
		#log-dhcp
		log-facility=$CONFDIR/dnsmasq.log
		bogus-priv
		domain-needed
	EOF
    # 'log-dhcp'(Extra logging for DHCP) shows too much logs.
    # if use '-d', 'log-facility' should = /dev/null
    if [[ $SHARE_METHOD == "none" ]]; then    
        echo "no-resolv"  >> "$CONFDIR/dnsmasq.conf"
        echo "no-poll" >> "$CONFDIR/dnsmasq.conf"
    fi
    if [[ "$DHCP_DNS" != "no" ]]; then
        if [[ "$DHCP_DNS" == "gateway" ]]; then
            dns_offer="$GATEWAY"
        else
            dns_offer="$DHCP_DNS"
        fi
        echo "dhcp-option-force=option:dns-server,${dns_offer}" >> "$CONFDIR/dnsmasq.conf"
    fi
    
    if [[ ! "$dnsmasq_NO_DNS" -eq 0 ]]; then
        echo "port=0"  >> "$CONFDIR/dnsmasq.conf"
    fi

    [[ -n "$MTU" ]] && echo "dhcp-option-force=option:mtu,${MTU}" >> "$CONFDIR/dnsmasq.conf"
    [[ $ETC_HOSTS -eq 0 ]] && echo no-hosts >> "$CONFDIR/dnsmasq.conf"
    [[ -n "$ADDN_HOSTS" ]] && echo "addn-hosts=${ADDN_HOSTS}" >> "$CONFDIR/dnsmasq.conf"
    if [[ "$THISHOSTNAME" ]]; then
        [[ "$THISHOSTNAME" == "-" ]] && THISHOSTNAME="$(cat /etc/hostname)"
        echo "interface-name=$THISHOSTNAME,$SUBNET_IFACE" >> "$CONFDIR/dnsmasq.conf"
    fi
    if [[ ! "$SHOW_DNS_QUERY" -eq 0 ]]; then
        echo log-queries=extra >> "$CONFDIR/dnsmasq.conf"
    fi
    
    if [[ $DNS ]]; then
        DNS_count=$(echo "$DNS" | awk -F, '{print NF}')
        for (( i=1;i<=DNS_count;i++ )); do
            sep_ip_port "$(echo $DNS | cut -d, -f$i)" DNS_IP DNS_PORT
            [[ "$DNS_PORT" ]] && DNS_PORT_D="#$DNS_PORT"
            echo "server=${DNS_IP}${DNS_PORT_D}" >> "$CONFDIR/dnsmasq.conf"
        done
        
        cat <<- EOF >> "$CONFDIR/dnsmasq.conf"
			no-resolv
			no-poll
		EOF
    fi
    if [[ $DNS_NOCACHE -eq 1 ]]; then
        echo "cache-size=0" >> "$CONFDIR/dnsmasq.conf"
        echo "no-negcache" >> "$CONFDIR/dnsmasq.conf"
    fi
    if [[ $IPV6 -eq 1 ]];then
        cat <<- EOF  >> "$CONFDIR/dnsmasq.conf"
			listen-address=${GATEWAY6}
			enable-ra
			#quiet-ra
			dhcp-range=interface:${SUBNET_IFACE},::,::ffff:ffff:ffff:ffff,constructor:${SUBNET_IFACE},ra-stateless,64
		EOF
        if [[ "$DHCP_DNS6" != "no" ]]; then
            if [[ "$DHCP_DNS6" == "gateway" ]]; then
                dns_offer6="[$GATEWAY6]"
            else
                dns_offer6="$DHCP_DNS6"
            fi
            echo "dhcp-option=option6:dns-server,${dns_offer6}" >> "$CONFDIR/dnsmasq.conf"
        fi
    fi
}

run_wifi_ap_processes() {
    if [[ $NO_HAVEGED -eq 0 ]]; then
        haveged_watchdog &
        HAVEGED_WATCHDOG_PID=$!
        echo "$HAVEGED_WATCHDOG_PID" > "$CONFDIR/haveged_watchdog.pid"
        echo
        echo "haveged_watchdog PID: $HAVEGED_WATCHDOG_PID" 
    fi

    # start access point
    #echo "hostapd command-line interface: hostapd_cli -p $CONFDIR/hostapd_ctrl"
    # start hostapd (use stdbuf when available for no delayed output in programs that redirect stdout)
    STDBUF_PATH=`which stdbuf`
    if [ $? -eq 0 ]; then
        STDBUF_PATH=$STDBUF_PATH" -oL"
    fi
    echo 
    echo "Starting hostapd"
    
    if which complain > /dev/null 2>&1; then
        complain hostapd
    fi
    
    # hostapd '-P' works only when use '-B' (run in background)
    $STDBUF_PATH hostapd $HOSTAPD_DEBUG_ARGS -P "$CONFDIR/hostapd.pid" "$CONFDIR/hostapd.conf"  &
    HOSTAPD_PID=$!
    echo "$HOSTAPD_PID" > "$CONFDIR/hostapd.pid"
    echo "hostapd PID: $HOSTAPD_PID"
    #while [[ ! -f $CONFDIR/hostapd.pid ]]; do
    #    sleep 1
    #done
    #echo -n "hostapd PID: " ; cat $CONFDIR/hostapd.pid
    pid_watchdog $HOSTAPD_PID 10 "hostapd failed" &
    sleep 3
}

start_dnsmasq() {
    echo 
    echo "Starting dnsmasq"
    
    if which complain > /dev/null 2>&1; then
        # openSUSE's apparmor does not allow dnsmasq to read files.
        # remove restriction.
        complain dnsmasq
    fi
    
    # Using '-d'(no daemon) dnsmasq will not turn into 'nobody'
    # '-x' works only when no '-d'
    dnsmasq  -k -C "$CONFDIR/dnsmasq.conf" -x "$CONFDIR/dnsmasq.pid" -l "$CONFDIR/dnsmasq.leases" & 
    #####DNSMASQ_PID=$!         # only when with '-d'
    ######echo "dnsmasq PID: $DNSMASQ_PID"      # only when with '-d'
    i=0; while [[ ! -f "$CONFDIR/dnsmasq.pid" ]]; do
        sleep 1
        i=$((i + 1))
        if [[ $i -gt 10 ]]; then die "Couldn't get dnsmasq PID" ; fi
    done
    DNSMASQ_PID="$(cat "$CONFDIR/dnsmasq.pid" )"
    echo  "dnsmasq PID: $DNSMASQ_PID" 
    ######(wait $DNSMASQ_PID ; die "dnsmasq failed") &  # wait can't deal with non-child
    pid_watchdog $DNSMASQ_PID 9 "dnsmasq failed" &
    sleep 2
}

check_rfkill_unblock_wifi() {
    local PHY
    if which rfkill > /dev/null 2>&1 ; then
        PHY=$(get_interface_phy_device ${SUBNET_IFACE})
        [[ -n $PHY ]] && rfkill unblock $(rfkill | grep $PHY | awk '{print $1}') >/dev/null 2>&1
    fi
}

#=========== Above are functions ======================
#=========== Executing begin ==============================

# if empty option, show usage and exit 
check_empty_option "$@"

# TODO: are some global variables are still defined in those following code?
define_global_variables

ARGS=( "$@" )

parse_user_options "$@"
# TODO: detect user option conflict

# check if networkManager running
NM_RUNNING="$(is_nm_running)"

TMPDIR="$(decide_tmpdir)"

# if user choose to deal with running instances, will output some info then exit after this 
# NOTE above don't require root
check_other_functions 
# NOTE below require root

# if user choose to daemonize, will start new background process and exit this 
daemonizing_check

# check if wifi will work on this system and user settings
[[ $WIFI_IFACE ]] && check_wifi_settings

[[ -n "$NEW_MACADDR" ]] && check_if_new_mac_valid # check NEW_MACADDR. will exit if not valid

# checks finished

## ===== Above don't echo anything if no warning or error====================
## ========================================================
phead
phead2
echo

echo "PID: $$"

TARGET_IFACE="$(decide_target_interface)" || exit 1 # judge wired (-i CONN_IFACE) or wireless hotspot (--ap $WIFI_IFACE)
echo "Target interface is ${TARGET_IFACE} ($(get_interface_mac $TARGET_IFACE)) $(get_interface_pci_info $TARGET_IFACE)"

if [[ "$MAC_USE_RANDOM" -eq 1 ]] ; then
    NEW_MACADDR="$(generate_random_mac)"
    echo "Use random MAC address $NEW_MACADDR"
fi

decide_ip_addresses # ip 4 & 6 lan addresses

# if user choose to make DHCP to tell clients to use other DNS, we don't have to serve DNS
[[ $DHCP_DNS != 'gateway' && $DHCP_DNS6 != 'gateway' ]] && dnsmasq_NO_DNS=1

#===========================================================
#==== begin to do some change on config files and system===

init_trap
# NOTE function die() is designed not to be used before init_trap() executed

init_conf_dirs #   CONFDIR  , COMMON_CONFDIR  . make dir

[[ $WIFI_IFACE ]] && prepare_wifi_interface # this will create virtual ap interface (if needed) and set VWIFI_IFACE and AP_IFACE (if success)

SUBNET_IFACE="$(decide_subnet_interface)"  # SUBNET_IFACE can be TARGET_IFACE (wired) or AP_IFACE (ap) .this is after prepare_wifi_interface()
echo "$SUBNET_IFACE" > "$CONFDIR/subn_iface"

# if virtual wifi interface, will be destroyed, so only need to save status when not
[[ -z $VWIFI_IFACE ]] && backup_interface_status

# TODO: should these 2 before calling prepare_wifi_interface ? in check_wifi_settings() ?
# set iw country code
if [[ $WIFI_IFACE && -n "$COUNTRY" && $USE_IWCONFIG -eq 0 ]]; then
    iw reg set "$COUNTRY" || die "Failed setting country code"
fi

# judge channel availability after changing country code
if [[ $WIFI_IFACE ]] ; then
    can_transmit_to_channel ${AP_IFACE} ${CHANNEL} || die "Your adapter can not transmit to channel ${CHANNEL}, frequency band ${FREQ_BAND}GHz."
fi

[[ $WIFI_IFACE ]] && write_hostapd_conf
#===================================================
#===================================================

# set interface unmanaged by networkManager
if [[ $NM_RUNNING -eq 1 ]] && nm_knows $TARGET_IFACE; then # if nm knows target iface, should know subnet iface too. but need to wait until nm finds subnet iface (waiting code is in nm_set_unmanaged()
    nm_set_unmanaged ${SUBNET_IFACE} # will write NM_UNM_LIST
fi

[[ $NO_DNSMASQ -eq 0 ]] && write_dnsmasq_conf
#===========================

# initialize subnet interface
# take subnet interface down first
ip link set down dev ${SUBNET_IFACE} || die "Failed setting ${SUBNET_IFACE} down"
# flush old IPs of subnet interface
ip addr flush ${SUBNET_IFACE} || die "Failed flush ${SUBNET_IFACE} IP"

dealwith_mac # setting MAC should be after setting NM unmanaged

[[ $WIFI_IFACE ]] && check_rfkill_unblock_wifi

# bring subnet interface up
ip link set up dev ${SUBNET_IFACE} || die "Failed bringing ${SUBNET_IFACE} up"

# hostapd , haveged
[[ $WIFI_IFACE ]] && run_wifi_ap_processes

# add ipv4 address to subnet interface
ip -4 addr add ${GATEWAY}/24 broadcast ${GATEWAY%.*}.255 dev ${SUBNET_IFACE} || die "Failed setting ${SUBNET_IFACE} IPv4 address"

set_ipv6_bits

# add ipv6 address to subnet interface
if [[ $IPV6 -eq 1 ]] ; then
    ip -6 addr add ${GATEWAY6}/64  dev ${SUBNET_IFACE} || die "Failed setting ${SUBNET_IFACE} IPv6 address"
fi

check_iptables

echo "NOTICE: Not showing all operations done to iptables rules"

[[ "$NO4" -eq 1 ]] && echo -e "\nWARN: Since you're using in this mode (no IPv4 Internet), make sure you've read Notice 1\n" >&2

# enable Internet sharing
if [[ "$SHARE_METHOD" == "none" ]]; then

    echo "No Internet sharing"
    
    echo -e "\nWARN: Since you're using in this mode (no Internet share), make sure you've read Notice 1\n" >&2
    
    [[ "$BANLAN" -eq 1 ]] && start_ban_lan
    
elif [[ "$SHARE_METHOD" == "nat" ]]; then

    [[ "$INTERNET_IFACE" ]] && echo -e "\nWARN: Since you're using in this mode (specify Internet interface), make sure you've read Notice 1\n" >&2

    [[ "$INTERNET_IFACE" && "$dnsmasq_NO_DNS" -eq 0 ]] && echo -e "\nWARN: You specified Internet interface but this host is providing local DNS. In some unexpected case (eg. mistaken configurations), queries may leak to other interfaces, which you should be aware of.\n" >&2
    
    start_nat
    
    [[ "$BANLAN" -eq 1 ]] && start_ban_lan
    
    echo 1 > "/proc/sys/net/ipv4/ip_forward" || die "Failed enabling system ipv4 forwarding" # TODO maybe uneeded in '--no4' mode
    
    if [[ $IPV6 -eq 1 ]]; then
        echo 1 > "/proc/sys/net/ipv6/conf/all/forwarding" || die "Failed enabling system ipv6 forwarding" # TODO if '-o' used, set only 2 interfaces' bits
    fi
    
    # to enable clients to establish PPTP connections we must
    # load nf_nat_pptp module
    modprobe nf_nat_pptp > /dev/null 2>&1 && echo "Loaded kernel module nf_nat_pptp"
    
elif [[ "$SHARE_METHOD" == "redsocks" ]]; then

    if [[ $IPV6 -eq 1 ]]; then
        echo 1 > "/proc/sys/net/ipv6/conf/$SUBNET_IFACE/forwarding" || die "Failed enabling $SUBNET_IFACE ipv6 forwarding" # to set NA router bit
    fi
    
    [[ "$dnsmasq_NO_DNS" -eq 0 && ! $DNS ]] &&  echo -e "\nWARN: You are using in transparent proxy mode but this host is providing local DNS. In some unexpected case (eg. mistaken configurations), queries may leak to other interfaces, which you should be aware of.\n" >&2

    [[ "$BANLAN" -eq 1 ]] && start_ban_lan
    
    start_redsocks
fi

# start dhcp + dns (optional)

# allow dns port input even if we don't run dnsmasq
# user can serve their own dns server
[[ "$DHCP_DNS" == "gateway" || "$DHCP_DNS6" == "gateway" ]] && allow_dns_port

[[ "$CATCH_DNS" -eq 1 ]] && start_catch_dns

[[ $NO_DNSMASQ -eq 0 ]] && ( allow_dhcp ; start_dnsmasq )

echo 
echo "== Setting up completed, now linux-router should be working =="


sudo ifconfig $WIFI_IFACE up 
#============================================================
#============================================================
#============================================================

show_qr() {
    local T S P H
    S="$SSID"
    if [[ -n "$PASSPHRASE" ]]; then
        T="WPA"
        P="$PASSPHRASE"
    else
        T="nopass"
    fi
    [[ "$HIDDEN" -eq 1 ]] && H="true"
    echo "Scan QR code on phone to connect to WiFi"
    qrencode -m 2 -t ANSIUTF8 "WIFI:T:${T};S:${S};P:${P};H:${H};"
    echo "Use this command to save QR code to image file:"
    echo "    qrencode -m 2 -o <file> \"WIFI:T:${T};S:${S};P:${P};H:${H};\""
    echo
}

[[ "$QR" -eq 1 ]] && show_qr

# need loop to keep this script running
bash -c "while :; do sleep 8000 ; done " &
KEEP_RUNNING_PID=$!
echo "$KEEP_RUNNING_PID" > "$CONFDIR/keep_running.pid"
wait $KEEP_RUNNING_PID

clean_exit