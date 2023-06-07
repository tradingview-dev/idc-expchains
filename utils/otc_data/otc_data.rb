#!/bin/env ruby

require 'optparse'
require 'net/http'
require 'typhoeus'
require 'json'

PARALLEL_REQUESTS = 1
Typhoeus::Config.user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"

Typhoeus.before do |request|
  sleep 0.5
end

class OtcDataDownloader

    def initialize(options = {})
    end

    def get_directory_url(page)
        pageSize = 25
        uri = URI("https://backend.otcmarkets.com/otcapi/company-directory?page=#{page}&pageSize=#{pageSize}")
        #puts uri
        return uri
    end
    def get_directory(page)
        uri = get_directory_url(page)
        result = `curl -s '#{uri.to_s}' -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0' -H 'Accept: application/json, text/plain, */*' -H 'Accept-Language: en,ru;q=0.7,en-US;q=0.3' --compressed -H 'Origin: https://www.otcmarkets.com' -H 'Referer: https://www.otcmarkets.com/' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache'`
        return JSON.parse(result)
    end

    def get_all_records_parallel()
        hydra = Typhoeus::Hydra.new(:max_concurrency => PARALLEL_REQUESTS)

        first_page = get_directory(1)
        pages = first_page["pages"]
        records = []
        records += (first_page["records"] || [])

        requests = []
        for p in 2..pages
            uri = get_directory_url(p)
            r = Typhoeus::Request.new(uri,
                headers: {
#                  'User-Agent' => 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0',
                  'Accept' => 'application/json, text/plain, */*',
                  'Accept-Language' => 'en,ru;q=0.7,en-US;q=0.3',
                  'Origin' => 'https://www.otcmarkets.com',
                  'Referer' => 'https://www.otcmarkets.com/',
                  'Pragma' => 'no-cache',
                  'Cache-Control' => 'no-cache',
                },
                followlocation: true,
                method: :get)
            requests << r
            hydra.queue(r)
        end
        hydra.run

        new_records = process_retry_parallel(requests, 5)
        records += new_records
        return records
    end

    def process_retry_parallel(requests, tries_left)
        records = []
        retry_list = []
        requests.each do |request|
            if request.response.code != 200
                if tries_left > 0
                    STDERR.puts "ERR #{request.response.code} on #{request.url} tries left #{tries_left}"
                    retry_list << request
                else
                    STDERR.puts "ERR #{request.response.code} on #{request.url}"
                end
                next
            end
            if request.response.body.empty?
                next
            end
            data = JSON.parse(request.response.body)
            records += (data["records"] || [])
        end

        if !retry_list.empty?
            sleep(30)
            hydra = Typhoeus::Hydra.new(:max_concurrency => PARALLEL_REQUESTS)
            retry_requests = []
            retry_list.each do |r|
                r = Typhoeus::Request.new(r.base_url,
                    followlocation: true,
                    method: :get)
                retry_requests << r
                hydra.queue(r)
            end
            hydra.run
            retry_records = process_retry_parallel(retry_requests, tries_left-1)
            return records + retry_records
        end

        return records
    end

    def get_all_records()
        first_page = get_directory(1)
        pages = first_page["pages"]
        records = []
        records += (first_page["records"] || [])

        for p in 2..pages
            page = get_directory(p)
            records += (page["records"] || [])
        end
        return records
    end

end


def mergeRecords(prevRecords, newRecords, field)
    newRecordsMap = {}
    newRecords.each do |r|
        newRecordsMap[r[field]] = r
    end

    prevRecords.each do |r|
        if newRecordsMap[r[field]].nil?
        newRecords << r
        end
    end

    newRecords.sort_by! {|r| r[field]}

    return newRecords
end

if __FILE__ == $0

        options = {
            :mergeFile => nil
        }

        OptionParser.new do |opts|
            opts.on("--merge FILE", "merge with file") do |v|
                options[:mergeFile] = v
            end
        end.parse!

        requester = OtcDataDownloader.new(options)
        records = requester.get_all_records_parallel()
        records.each do |r|
            r.delete("joined")
            r.delete("marketCap")
        end

        if !options[:mergeFile].nil?
            prevRecords = JSON.parse(File.read(options[:mergeFile]))
            records = mergeRecords(prevRecords, records, "symbol")
        end
        puts records.to_json()
end
